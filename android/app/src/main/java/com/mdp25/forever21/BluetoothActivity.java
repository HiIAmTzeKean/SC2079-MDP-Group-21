package com.mdp25.forever21;

import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.annotation.NonNull;
import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;
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
import com.mdp25.forever21.bluetooth.BluetoothMessage;
import com.mdp25.forever21.bluetooth.BluetoothMessageParser;
import com.mdp25.forever21.bluetooth.BluetoothMessageReceiver;

import java.util.ArrayList;

public class BluetoothActivity extends AppCompatActivity {

    private static final String TAG = "BluetoothActivity";
    private static final int BLUETOOTH_PERMISSIONS_REQUEST_CODE = 96;
    private static final int DISCOVERABLE_DURATION = 300;
    private MyApplication myApp; // my context for "static" vars
    private BroadcastReceiver broadcastReceiver; //main receiver for all bt intents
    private BluetoothMessageReceiver msgReceiver; //receive bluetooth messages
    private BluetoothDeviceAdapter bluetoothDeviceAdapter; // to inflate recycler view

    // UI variables below
    private TextView receivedMsgView;
    private TextView statusView;
    private TextInputEditText msgInput;

    @SuppressLint("UnspecifiedRegisterReceiverFlag")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_bluetooth);

        // retrieve bluetooth adapter
        myApp = (MyApplication) getApplication();

        //TODO disable back button from gg back to InitActivity...
        //getOnBackPressedDispatcher().addCallback(callback -> {} );

        // first ensure bluetooth is enabled
        if (!myApp.btInterface().isBluetoothEnabled()) {
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
        enableDeviceDiscovery();

        // find all views and bind them appropriately
        bindUI();

        // register broadcast receivers for bluetooth context
        this.broadcastReceiver = new BroadcastReceiver() {
            @Override
            public void onReceive(Context context, Intent intent) {
                onBroadcastReceived(context, intent);
            }
        };
        IntentFilter[] intentFilters = new IntentFilter[]{
                new IntentFilter(BluetoothDevice.ACTION_FOUND), //discovered a device
                new IntentFilter(BluetoothDevice.ACTION_BOND_STATE_CHANGED), // connected/disconnected
                new IntentFilter(BluetoothAdapter.ACTION_SCAN_MODE_CHANGED), //scan on/off
                new IntentFilter(BluetoothAdapter.ACTION_STATE_CHANGED), // bt on/off
//                new IntentFilter(BluetoothConnection.ACTION_CONNECTION_STATE), // connected/disconnected, not rlly needed
        }; //for broadcastReceiver
        for (IntentFilter intentFilter : intentFilters) {
            getApplicationContext().registerReceiver(broadcastReceiver, intentFilter);
        }

        // register message receiver
        msgReceiver = new BluetoothMessageReceiver(BluetoothMessageParser.ofDefault(), this::onMsgReceived);
        getApplicationContext().registerReceiver(msgReceiver, new IntentFilter(BluetoothMessageReceiver.ACTION_MSG_READ));
    }

    private void bindUI() {
        // bind UI to methods
        RecyclerView recyclerView = findViewById(R.id.btDeviceList);
        recyclerView.setLayoutManager(new LinearLayoutManager(this));
        bluetoothDeviceAdapter = new BluetoothDeviceAdapter(this, new ArrayList<>(), device -> {
            Toast.makeText(this, "Clicked: " + device.name(), Toast.LENGTH_SHORT).show();
            myApp.btInterface().connectAsClient(device.btDevice());
        });
        recyclerView.setAdapter(bluetoothDeviceAdapter);
        findViewById(R.id.btnScan).setOnClickListener(view -> myApp.btInterface().scanForDevices());

        // these should be moved to CanvasActivity eventually
        receivedMsgView = findViewById(R.id.textRecievedMsg);
        receivedMsgView.setText("Received Messages:\n");
        statusView = findViewById(R.id.textStatus);
        msgInput = findViewById(R.id.msgInput);
        findViewById(R.id.btnSend).setOnClickListener(view -> {
            if (msgInput.getText() != null) {
                String s = msgInput.getText().toString();
                if (!s.isEmpty()) {
                    myApp.btConnection().sendMessage(msgInput.getText().toString());
                }
            }
        });
        findViewById(R.id.btnRobotForward).setOnClickListener(view -> myApp.btConnection().sendMessage("f"));
        findViewById(R.id.btnRobotBackward).setOnClickListener(view -> myApp.btConnection().sendMessage("r"));
        findViewById(R.id.btnRobotRight).setOnClickListener(view -> myApp.btConnection().sendMessage("tr"));
        findViewById(R.id.btnRobotLeft).setOnClickListener(view -> myApp.btConnection().sendMessage("tl"));
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        getApplicationContext().unregisterReceiver(broadcastReceiver);
        getApplicationContext().unregisterReceiver(msgReceiver);
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

    private void enableDeviceDiscovery() {
        Intent discoverableIntent = new Intent(BluetoothAdapter.ACTION_REQUEST_DISCOVERABLE);
        discoverableIntent.putExtra(BluetoothAdapter.EXTRA_DISCOVERABLE_DURATION, DISCOVERABLE_DURATION);
        ActivityResultLauncher<Intent> requestDiscoverable = registerForActivityResult(
                new ActivityResultContracts.StartActivityForResult(),
                result -> {
                    if (result.getResultCode() == Activity.RESULT_OK) {
                        Log.d(TAG, "Bluetooth Discovery on for " + DISCOVERABLE_DURATION + "s");
                    }
                });
        requestDiscoverable.launch(discoverableIntent);
    }


    // starts scanning / connecting to devices
    private void startBluetooth() {
        if (myApp.btInterface().isBluetoothEnabled()) {
            // add all paired devices to device list
            bluetoothDeviceAdapter.initPairedDevices(myApp.btInterface().getBondedDevices());
            // accept any incoming bt connections
            myApp.btInterface().acceptIncomingConnection();
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
        Log.d(TAG, "Received broadcast: " + intent.getAction());
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
                            myApp.btInterface().acceptIncomingConnection();
                            enableDeviceDiscovery();
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

    private void onMsgReceived(BluetoothMessage btMsg) {
        if (btMsg instanceof BluetoothMessage.PlainStringMessage m) {
            receivedMsgView.append(m.rawMsg() + "\n");
        } else if (btMsg instanceof BluetoothMessage.RobotStatusMessage m) {
            statusView.setText(m.status());
        } else if (btMsg instanceof BluetoothMessage.TargetFoundMessage m) {
            //TODO
        } else if (btMsg instanceof BluetoothMessage.RobotPositionMessage m) {
            //TODO
        }
    }
}