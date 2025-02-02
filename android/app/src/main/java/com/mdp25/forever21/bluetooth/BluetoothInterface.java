package com.mdp25.forever21.bluetooth;

import android.Manifest;
import android.annotation.SuppressLint;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothManager;
import android.bluetooth.BluetoothServerSocket;
import android.bluetooth.BluetoothSocket;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.pm.PackageManager;
import android.util.Log;

import androidx.core.app.ActivityCompat;

import java.io.IOException;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

/**
 * Class which creates bluetooth connections. Assumes appropriate bluetooth permissions have been granted.
 *
 * <p> References: <a href = "https://developer.android.com/develop/connectivity/bluetooth/connect-bluetooth-devices#java">Connect BT devices</a>,
 * <a href = "https://developer.android.com/develop/connectivity/bluetooth/find-bluetooth-devices">Find BT devices</a>
 */
public class BluetoothInterface {
    private static final String TAG = "BluetoothInterface";
    private static final String BT_NAME = "MDP_GRP_21";
    private static final UUID BT_UUID = UUID.fromString("00001101-0000-1000-8000-00805F9B34FB"); // standard SerialPortServiceClass UUID?

    private final Context context; //read-only, used by child threads
    private final BluetoothAdapter bluetoothAdapter; //read-only, used by child threads

    private AcceptThread acceptThread = null; // thread that accepts and incoming bt connection
    private ConnectThread connectThread = null; // thread that scans for devices to connect to
    private BluetoothConnection btConnection = null; // resulting bluetooth connection handler

    private Lock threadLock; // to lock acceptThread and connectThread read/write
    private Lock connectionLock; // to lock btConnection

    private BroadcastReceiver broadcastReceiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            onBroadcastReceived(context, intent);
        }
    };

    private IntentFilter[] intentFilters = new IntentFilter[]{
            new IntentFilter(BluetoothDevice.ACTION_FOUND), //discovered a device
            new IntentFilter(BluetoothDevice.ACTION_BOND_STATE_CHANGED), // connected/disconnected
            new IntentFilter(BluetoothAdapter.ACTION_SCAN_MODE_CHANGED), //scan on/off
            new IntentFilter(BluetoothAdapter.ACTION_STATE_CHANGED), // bt on/off
    }; //for broadcastReceiver

    public BluetoothInterface(Context context) {
        BluetoothManager btMgr = (BluetoothManager) context.getSystemService(Context.BLUETOOTH_SERVICE);
        this.bluetoothAdapter = btMgr.getAdapter();
        this.context = context;

        threadLock = new ReentrantLock();
        connectionLock = new ReentrantLock();
    }

    // this method runs when a connection is made
    void onConnected(BluetoothSocket socket, BluetoothDevice device) {
        threadLock.lock();
        try {
            if (acceptThread != null) {
                acceptThread.cancel();
                acceptThread = null;
            }
            if (connectThread != null) {
                connectThread.cancel();
                connectThread = null;
            }
        } finally {
            threadLock.unlock();
        }

        connectionLock.lock();
        try {
            this.btConnection = new BluetoothConnection(context, socket, device);
            btConnection.start();
        } finally {
            connectionLock.unlock();
        }
    }

    public boolean isBluetoothEnabled() {
        return bluetoothAdapter.isEnabled();
    }

    public BroadcastReceiver getBroadcastReceiver() {
        return broadcastReceiver;
    }

    /**
     * For registering {@link #getBroadcastReceiver()}.
     */
    public IntentFilter[] getIntentFilters() {
        return intentFilters;
    }

    /**
     * Use this getter to retrieve a {@link BluetoothConnection} to send messages etc.
     */
    public BluetoothConnection getBluetoothChannel() {
        return btConnection;
    }

    /**
     * I.e. starts the {@link AcceptThread} (and stops the {@link ConnectThread})
     */
    public void acceptIncomingConnection() {
        threadLock.lock();
        try {
            if (connectThread != null) {
                connectThread.cancel();
                connectThread = null;
            }
            if (acceptThread == null) {
                acceptThread = new AcceptThread();
                acceptThread.start();
            }
        } finally {
            threadLock.unlock();
        }
    }

    /**
     * I.e. starts the {@link ConnectThread} (and stops the {@link AcceptThread})
     */
    public void connectAsClient(BluetoothDevice btDevice) {
        threadLock.lock();
        try {
            if (acceptThread != null) {
                acceptThread.cancel();
                acceptThread = null;
            }
            if (connectThread == null) {
                connectThread = new ConnectThread(btDevice);
                connectThread.start();
            }
        } finally {
            threadLock.unlock();
        }
    }

    /**
     * Scans for bluetooth devices
     * TODO decide how to return
     */
    @SuppressLint("MissingPermission")
    public void scanForDevices() {
        if (bluetoothAdapter.isDiscovering()) {
            bluetoothAdapter.cancelDiscovery();
            bluetoothAdapter.startDiscovery();
            Log.d(TAG, "Starting Bluetooth discovery");
        }
        Set<BluetoothDevice> pairedDevices = bluetoothAdapter.getBondedDevices();
        for (BluetoothDevice device : pairedDevices) {
            Log.d(TAG, "Paired device : " + device.getName());
        }
    }

    // code from android docs
    private class AcceptThread extends Thread {
        private final BluetoothServerSocket serverSocket;

        @SuppressLint("MissingPermission")
        public AcceptThread() {
            BluetoothServerSocket tmp = null;
            try {
                tmp = bluetoothAdapter.listenUsingRfcommWithServiceRecord(BT_NAME, BT_UUID);
//                tmp = bluetoothAdapter.listenUsingInsecureRfcommWithServiceRecord(BT_NAME, BT_UUID);

            } catch (IOException e) {
                Log.e(TAG, "Socket's listen() method failed", e);
            }
            this.serverSocket = tmp;
        }

        @Override
        public void run() {
            Log.d(TAG, "AcceptThread: Running.");
            BluetoothSocket socket = null;
            while (true) {
                try {
                    socket = serverSocket.accept();
                } catch (IOException e) {
                    Log.e(TAG, "Socket's accept() method failed", e);
                    break;
                }

                if (socket != null) {
                    onConnected(socket, socket.getRemoteDevice());
                    try {
                        serverSocket.close();
                    } catch (IOException e) {
                        throw new RuntimeException(e);
                    }
                    break;
                }
            }
        }

        // Closes the connect socket and causes the thread to finish.
        public void cancel() {
            try {
                serverSocket.close();
                Log.d(TAG, "AcceptThread: Socket closed.");
            } catch (IOException e) {
                Log.e(TAG, "Could not close the AcceptThread socket", e);
            }
            this.interrupt();
        }
    }

    private class ConnectThread extends Thread {
        private final BluetoothSocket socket;
        private final BluetoothDevice device;

        @SuppressLint("MissingPermission")
        public ConnectThread(BluetoothDevice device) {
            BluetoothSocket tmp = null;
            this.device = device;

            try {
                tmp = device.createRfcommSocketToServiceRecord(BT_UUID);

            } catch (IOException e) {
                Log.e(TAG, "Socket's create() method failed", e);
            }
            this.socket = tmp;
        }

        @SuppressLint("MissingPermission")
        @Override
        public void run() {
            Log.d(TAG, "ConnectThread: Running.");
            // cancel discovery because it slows down the connection
            bluetoothAdapter.cancelDiscovery();

            try {
                socket.connect();
            } catch (IOException connectException) {
                // unable to connect
                try {
                    socket.close();
                } catch (IOException closeException) {
                    Log.e(TAG, "Could not close the client socket", closeException);
                }
                return;
            }

            onConnected(socket, device);
        }

        public void cancel() {
            try {
                socket.close();
                Log.d(TAG, "ConnectThread: Socket closed.");
            } catch (IOException e) {
                Log.e(TAG, "Could not close the ConnectThread socket", e);
            }
            this.interrupt();
        }
    }

    @SuppressLint("MissingPermission")
    private void onBroadcastReceived(Context context, Intent intent) {
        String action = intent.getAction();
        switch (action) {
            case BluetoothDevice.ACTION_FOUND -> {
                // Discovery has found a device. Get the BluetoothDevice
                // object and its info from the Intent.
                BluetoothDevice device = intent.getParcelableExtra(BluetoothDevice.EXTRA_DEVICE, BluetoothDevice.class);
                String deviceName = device.getName();
                String deviceHardwareAddress = device.getAddress(); // MAC address
                Log.d(TAG, deviceName + ": " + deviceHardwareAddress);
            }
            //TODO
            default -> {
                Log.d(TAG, "Unknown action received in onBroadcastReceived.");
            }
        }
    }
}
