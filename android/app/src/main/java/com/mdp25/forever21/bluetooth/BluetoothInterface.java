package com.mdp25.forever21.bluetooth;

import android.annotation.SuppressLint;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothManager;
import android.bluetooth.BluetoothServerSocket;
import android.bluetooth.BluetoothSocket;
import android.content.Context;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import android.widget.Toast;

import java.io.IOException;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

/**
 * Class which creates the threads to accept bluetooth connections. Assumes appropriate bluetooth permissions have been granted.
 *
 * <p> References: <a href = "https://developer.android.com/develop/connectivity/bluetooth/connect-bluetooth-devices#java">Connect BT devices</a>,
 * <a href = "https://developer.android.com/develop/connectivity/bluetooth/find-bluetooth-devices">Find BT devices</a>
 */
public class BluetoothInterface {
    private static final String TAG = "BluetoothInterface";
    private static final String BT_NAME = "MDP_GRP_21";
    private static final UUID BT_UUID = UUID.fromString("00001101-0000-1000-8000-00805F9B34FB"); // standard SerialPortServiceClass UUID?

    private final Context context; //read-only, used by child threads
    private final BluetoothAdapter bluetoothAdapter; // adapter is already synchronized

    // note that AcceptThread and ConnectThread are not mutually exclusive,
    // but they share a lock for simplicity.
    // Both threads should be done when a BluetoothConnection is made.
    private AcceptThread acceptThread = null; // thread that accepts and incoming bt connection
    private ConnectThread connectThread = null; // thread that scans for devices to connect to
    private BluetoothConnection btConnection = null; // resulting bluetooth connection handler

    private final Lock threadLock; // to lock acceptThread and connectThread read/write
    private final Lock connectionLock; // to lock btConnection

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
        // close un-needed server sockets and resources
        // but importantly do not close BluetoothSocket!

        if (acceptThread != null) {
            acceptThread.cancel();
            acceptThread = null;
        }
        if (connectThread != null) {
            connectThread.cancel();
            connectThread = null;
        }

        connectionLock.lock();
        try {
            if (btConnection != null)
                btConnection.cancel();
            btConnection = new BluetoothConnection(context, socket, device);
            btConnection.start();
        } finally {
            connectionLock.unlock();
        }

        threadLock.unlock();
    }

    public boolean isBluetoothEnabled() {
        return bluetoothAdapter.isEnabled();
    }

    /**
     * Use this getter to retrieve a {@link BluetoothConnection} to send messages etc.
     */
    public BluetoothConnection getBluetoothConnection() {
        return btConnection;
    }

    /**
     * I.e. starts the {@link AcceptThread} (and stops the {@link ConnectThread})
     * <p> Make sure the device is discoverable in the first place for unpaired connection.
     */
    public void acceptIncomingConnection() {
        threadLock.lock();
        try {
            if (acceptThread != null) {
                acceptThread.cancel();
            }
            acceptThread = new AcceptThread();
            acceptThread.start();
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
            if (connectThread != null) {
                connectThread.cancel();
            }
            connectThread = new ConnectThread(btDevice);
            connectThread.start();
        } finally {
            threadLock.unlock();
        }
    }

    /**
     * Scans for bluetooth devices
     */
    @SuppressLint("MissingPermission")
    public void scanForDevices() {
        if (bluetoothAdapter.isDiscovering()) {
            bluetoothAdapter.cancelDiscovery();
        }
        boolean res = bluetoothAdapter.startDiscovery();
        if (!res) {
            Log.e(TAG, "bluetoothAdapter.startDiscovery() was false");
        }
        Toast.makeText(context, "Scanning for devices...", Toast.LENGTH_SHORT).show();
    }

    @SuppressLint("MissingPermission")
    public Set<BluetoothDevice> getBondedDevices() {
        return bluetoothAdapter.getBondedDevices();
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

        @SuppressLint("MissingPermission")
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
                    Log.d(TAG, "Socket Addr:" + socket.getRemoteDevice().getAddress());
                    Log.d(TAG, "Socket Name:" + socket.getRemoteDevice().getName());
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
                Log.d(TAG, "Socket Addr:" + socket.getRemoteDevice().getAddress());
                Log.d(TAG, "Socket Name:" + socket.getRemoteDevice().getName());
                onConnected(socket, device);
            } catch (IOException connectException) {
                // unable to connect
                try {
                    Log.e(TAG, "Unable to connect");
                    new Handler(Looper.getMainLooper()).post(() ->
                            Toast.makeText(context, "Connection failed", Toast.LENGTH_SHORT).show()
                    );
                    socket.close();
                } catch (IOException closeException) {
                    Log.e(TAG, "Could not close the client socket", closeException);
                }
            }
        }

        public void cancel() {
            // let other thread close the socket!
//            try {
//                //socket.close();
//                //Log.d(TAG, "ConnectThread: Socket closed.");
//            } catch (IOException e) {
//                Log.e(TAG, "Could not close the ConnectThread socket", e);
//            }
            this.interrupt();
        }
    }
}
