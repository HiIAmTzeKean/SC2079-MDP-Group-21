package com.mdp25.forever21;

import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.annotation.NonNull;
import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;
import androidx.localbroadcastmanager.content.LocalBroadcastManager;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import android.Manifest;
import android.annotation.SuppressLint;
import android.app.Activity;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Bundle;
import android.provider.Settings;
import android.util.Log;
import android.widget.TextView;
import android.widget.Toast;

import com.google.android.material.textfield.TextInputEditText;
import com.mdp25.forever21.bluetooth.BluetoothDeviceAdapter;
import com.mdp25.forever21.bluetooth.BluetoothDeviceModel;
import com.mdp25.forever21.bluetooth.BluetoothInterface;
import com.mdp25.forever21.bluetooth.BluetoothMessage;
import com.mdp25.forever21.bluetooth.BluetoothMessageParser;

import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import java.util.Set;

public class BluetoothActivity extends AppCompatActivity {

    private static final String TAG = "BluetoothActivity";
    private static final int BLUETOOTH_PERMISSIONS_REQUEST_CODE = 96;
    private static final int DISCOVERABLE_DURATION = 300;
    private BluetoothInterface bluetoothInterface;
    private BluetoothMessageParser parser;
    private BroadcastReceiver broadcastReceiver;
    private BluetoothDeviceAdapter bluetoothDeviceAdapter; // to inflate recycler view
    private BluetoothDeviceModel selectedDevice = null;

    // UI variables below
    private TextView receivedMsgView;
    private TextView statusView;
    private TextInputEditText msgInput;

    @SuppressLint("UnspecifiedRegisterReceiverFlag")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_bluetooth);

        //TODO disable back button from gg back to InitActivity...
        //getOnBackPressedDispatcher().addCallback(callback -> {} );

        parser = BluetoothMessageParser.ofDefault();

        // retrieve bluetooth adapter
        bluetoothInterface = new BluetoothInterface(this);

        // first ensure bluetooth is enabled
        if (!bluetoothInterface.isBluetoothEnabled()) {
            Toast.makeText(this, "This app requires Bluetooth to function.", Toast.LENGTH_SHORT).show();
            Intent enableBtIntent = new Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE);
            ActivityResultLauncher<Intent> requestEnableBluetooth = registerForActivityResult(
                    new ActivityResultContracts.StartActivityForResult(),
                    result -> {
                        if (result.getResultCode() == Activity.RESULT_OK) {
                            Log.d(TAG, "Bluetooth enabled.");
                        }
                    });
            requestEnableBluetooth.launch(enableBtIntent);
        }

        // then request bluetooth permissions
        String[] permissions = new String[]{
                Manifest.permission.BLUETOOTH_SCAN,
                Manifest.permission.BLUETOOTH_CONNECT,
                Manifest.permission.BLUETOOTH_ADVERTISE
        };
        requestPermissions(permissions, BLUETOOTH_PERMISSIONS_REQUEST_CODE);

        // make device discoverable
        //enableDeviceDiscovery(DISCOVERABLE_DURATION);

        // register broadcast receivers
        IntentFilter[] intentFilters = new IntentFilter[]{
                new IntentFilter(BluetoothDevice.ACTION_FOUND), //discovered a device
                new IntentFilter(BluetoothDevice.ACTION_BOND_STATE_CHANGED), // connected/disconnected
                new IntentFilter(BluetoothAdapter.ACTION_SCAN_MODE_CHANGED), //scan on/off
                new IntentFilter(BluetoothAdapter.ACTION_STATE_CHANGED), // bt on/off
        }; //for broadcastReceiver
        this.broadcastReceiver = new BroadcastReceiver() {
            @Override
            public void onReceive(Context context, Intent intent) {
                onBroadcastReceived(context, intent);
            }
        };
        for (IntentFilter intentFilter : intentFilters) {
            registerReceiver(broadcastReceiver, intentFilter);
        }

        // register a local receiver to handle messages
        LocalBroadcastManager localBroadcastManager = LocalBroadcastManager.getInstance(this);
        BroadcastReceiver msgReciever = new BroadcastReceiver() {
            @Override
            public void onReceive(Context context, Intent intent) {
                onMsgRecieved(context, intent);
            }
        };
        localBroadcastManager.registerReceiver(msgReciever, new IntentFilter(BluetoothMessage.INTENT_ACTION));


        // bind UI to methods
        RecyclerView recyclerView = findViewById(R.id.btDeviceList);
        recyclerView.setLayoutManager(new LinearLayoutManager(this));
        bluetoothDeviceAdapter = new BluetoothDeviceAdapter(this, new ArrayList<>(), device -> {
            Toast.makeText(this, "Clicked: " + device.name(), Toast.LENGTH_SHORT).show();
            selectedDevice = device;
            // todo handle connection
            // bluetoothInterface.connectAsClient(device);
        });
        recyclerView.setAdapter(bluetoothDeviceAdapter);
        findViewById(R.id.btnScan).setOnClickListener(view -> bluetoothInterface.scanForDevices());

        // these should be moved to CanvasActivity eventually
        msgInput = findViewById(R.id.msgInput);
        receivedMsgView = findViewById(R.id.textRecievedMsg);
        statusView = findViewById(R.id.textStatus);
        receivedMsgView.setText("Received Messages:\n");
        findViewById(R.id.btnSend).setOnClickListener(view -> bluetoothInterface.getBluetoothChannel().sendMessage(msgInput.getText().toString()));

        // this code below should be moved to RobotBluetoothComm eventually
        findViewById(R.id.btnRobotForward).setOnClickListener(view -> bluetoothInterface.getBluetoothChannel().sendMessage("f"));
        findViewById(R.id.btnRobotBackward).setOnClickListener(view -> bluetoothInterface.getBluetoothChannel().sendMessage("r"));
        findViewById(R.id.btnRobotRight).setOnClickListener(view -> bluetoothInterface.getBluetoothChannel().sendMessage("tr"));
        findViewById(R.id.btnRobotLeft).setOnClickListener(view -> bluetoothInterface.getBluetoothChannel().sendMessage("tl"));
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        // unregister all recievers
        unregisterReceiver(broadcastReceiver);
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == BLUETOOTH_PERMISSIONS_REQUEST_CODE) {
            boolean allPermissionsGranted = true;
            for (int result : grantResults) {
                if (result != PackageManager.PERMISSION_GRANTED) {
                    allPermissionsGranted = false;
                    break;
                }
            }

            if (allPermissionsGranted) {
                // permission all good, init bluetooth
                startBluetooth();
            } else {
                // ask user for permissions
                showPermissionDeniedDialog();
            }
        }
    }

    private void enableDeviceDiscovery(int duration) {
        Intent discoverableIntent = new Intent(BluetoothAdapter.ACTION_REQUEST_DISCOVERABLE);
        discoverableIntent.putExtra(BluetoothAdapter.EXTRA_DISCOVERABLE_DURATION, duration);
        ActivityResultLauncher<Intent> requestDiscoverable = registerForActivityResult(
                new ActivityResultContracts.StartActivityForResult(),
                result -> {
                    if (result.getResultCode() == Activity.RESULT_OK) {
                        Log.d(TAG, "Bluetooth Discovery on for " + duration + "s");
                    }
                });
        requestDiscoverable.launch(discoverableIntent);
    }


    // starts scanning / connecting to devices
    private void startBluetooth() {
        if (bluetoothInterface.isBluetoothEnabled()) {
            // add all paired devices to device list
            bluetoothDeviceAdapter.initPairedDevices(bluetoothInterface.getBondedDevices());
            // accept any incoming bt connections
            bluetoothInterface.acceptIncomingConnection();
        }
    }

    private void showPermissionDeniedDialog() {
        new AlertDialog.Builder(this)
                .setTitle("Bluetooth Permissions Required")
                .setMessage("This app needs Bluetooth permissions (i.e. Nearby Devices) to function properly. " +
                        "Please grant the permissions in Settings.")
                .setPositiveButton("Open Settings", (dialog, which) -> {
                    Intent intent = new Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS);
                    intent.setData(Uri.fromParts("package", getPackageName(), null));
                    startActivity(intent);
                })
                .setNegativeButton("Cancel", null)
                .show();
    }

    @SuppressLint("MissingPermission")
    private void onBroadcastReceived(Context context, Intent intent) {
        String action = intent.getAction();
        if (action == null)
            return;
        switch (action) {
            case BluetoothDevice.ACTION_FOUND -> {
                // discovered a bluetooth device
                BluetoothDevice device = intent.getParcelableExtra(BluetoothDevice.EXTRA_DEVICE, BluetoothDevice.class);
                if (device != null) {
                    String deviceName = device.getName();
                    String deviceHardwareAddress = device.getAddress(); // MAC address
                    Log.d(TAG, "Discovered " + deviceName + " (" + deviceHardwareAddress + ")");
                    bluetoothDeviceAdapter.addDiscoveredDevice(device);
                }
            }
            case BluetoothDevice.ACTION_BOND_STATE_CHANGED -> {
                BluetoothDevice device = intent.getParcelableExtra(BluetoothDevice.EXTRA_DEVICE, BluetoothDevice.class);
                if (device != null) {
                    switch (device.getBondState()) {
                        case BluetoothDevice.BOND_NONE -> {
                            Toast.makeText(this, String.format("%s disconnected, trying to reconnect...", device.getName()), Toast.LENGTH_SHORT).show();

                            // TODO try to reconnect?
                        }
                        case BluetoothDevice.BOND_BONDED ->
                                Toast.makeText(this, String.format("Connected to %s.", device.getName()), Toast.LENGTH_SHORT).show();
                        case BluetoothDevice.BOND_BONDING ->
                                Toast.makeText(this, String.format("Connecting to %s...", device.getName()), Toast.LENGTH_SHORT).show();

                    }
                }
            }
            case BluetoothAdapter.ACTION_SCAN_MODE_CHANGED -> {
                int mode = intent.getIntExtra(BluetoothAdapter.EXTRA_SCAN_MODE, BluetoothAdapter.ERROR);
                switch (mode) {
                    case BluetoothAdapter.SCAN_MODE_CONNECTABLE_DISCOVERABLE ->
                            Toast.makeText(this, "Bluetooth Discoverability is on.", Toast.LENGTH_LONG).show();
                    case BluetoothAdapter.SCAN_MODE_CONNECTABLE, BluetoothAdapter.SCAN_MODE_NONE ->
                            Toast.makeText(this, "Bluetooth Discoverability is now off.", Toast.LENGTH_LONG).show();
                }
            }
            case BluetoothAdapter.ACTION_STATE_CHANGED -> {
                int state = intent.getIntExtra(BluetoothAdapter.EXTRA_STATE, BluetoothAdapter.ERROR);
                switch (state) {
                    case BluetoothAdapter.STATE_OFF ->
                            Toast.makeText(this, "Bluetooth is turned off. Please turn it back on as this app requires Bluetooth to function.", Toast.LENGTH_LONG).show();
                    case BluetoothAdapter.STATE_ON ->
                            Toast.makeText(this, "Bluetooth turned on.", Toast.LENGTH_SHORT).show();
                }
            }
            default -> {
                Log.d(TAG, "Unknown action received in onBroadcastReceived.");
            }
        }
    }

    private void onMsgRecieved(Context context, Intent intent) {
        if (!Objects.equals(intent.getAction(), BluetoothMessage.INTENT_ACTION)) {
            return;
        }
        BluetoothMessage msg = intent.getParcelableExtra(BluetoothMessage.INTENT_EXTRA_NAME, BluetoothMessage.class);
        if (msg instanceof BluetoothMessage.StringMessage strMsg) {
            // TODO parse?
            receivedMsgView.append(strMsg.str());
        } else if (msg instanceof BluetoothMessage.StatusMessage statusMsg) {
            //TODO
        }
    }
}