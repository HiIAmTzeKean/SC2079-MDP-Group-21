package com.mdp25.forever21;

import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.annotation.NonNull;
import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
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
import android.location.LocationManager;
import android.net.Uri;
import android.os.Bundle;
import android.provider.Settings;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

import com.google.android.material.textfield.TextInputEditText;
import com.mdp25.forever21.bluetooth.BluetoothConnection;
import com.mdp25.forever21.bluetooth.BluetoothDeviceAdapter;
import com.mdp25.forever21.bluetooth.BluetoothInfoReceiver;
import com.mdp25.forever21.bluetooth.BluetoothMessage;
import com.mdp25.forever21.bluetooth.BluetoothMessageParser;
import com.mdp25.forever21.bluetooth.BluetoothMessageReceiver;

import java.util.ArrayList;

public class BluetoothActivity extends AppCompatActivity {

    private static final String TAG = "BluetoothActivity";
    private static final int BLUETOOTH_PERMISSIONS_REQUEST_CODE = 96;
    private static final int DISCOVERABLE_DURATION = 30;
    private MyApplication myApp; // my context for "static" vars
    private BroadcastReceiver infoReceiver; //main receiver for all bt intents
    private BroadcastReceiver msgReceiver; //receive bluetooth messages
    private BluetoothDeviceAdapter bluetoothDeviceAdapter; // to inflate recycler view

    private ActivityResultLauncher<Intent> requestEnableBluetooth; // to enable bluetooth
    private ActivityResultLauncher<Intent> requestDiscoverable; // to enable discovery

    // UI variables below
    private TextView receivedMsgView;
    private TextView statusView;
    private TextInputEditText msgInput;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_bluetooth);

        // retrieve bluetooth adapter
        myApp = (MyApplication) getApplication();

        //TODO disable back button from gg back to InitActivity...
        //getOnBackPressedDispatcher().addCallback(callback -> {} );

        // request bluetooth permissions
        String[] permissions = new String[]{
                Manifest.permission.BLUETOOTH_SCAN,
                Manifest.permission.BLUETOOTH_CONNECT,
                Manifest.permission.BLUETOOTH_ADVERTISE,
                Manifest.permission.ACCESS_FINE_LOCATION, // need location for scanning devices
                Manifest.permission.ACCESS_COARSE_LOCATION, // need location for scanning devices
        };
        requestPermissions(permissions, BLUETOOTH_PERMISSIONS_REQUEST_CODE);

        // find all views and bind them appropriately
        bindUI();

        // register request bluetooth
        requestEnableBluetooth = registerForActivityResult(
                new ActivityResultContracts.StartActivityForResult(),
                result -> {
                    if (result.getResultCode() == Activity.RESULT_OK) {
                        Log.d(TAG, "Bluetooth enabled.");
                        startBluetooth();
                    }
                });

        // register discoverable result
        requestDiscoverable = registerForActivityResult(
                new ActivityResultContracts.StartActivityForResult(),
                result -> {
                    if (result.getResultCode() == Activity.RESULT_OK) {
                        Log.d(TAG, "Bluetooth Discovery on for " + DISCOVERABLE_DURATION + "s");
                    }
                });

        // register broadcast receivers for bluetooth context
        infoReceiver = new BluetoothInfoReceiver(this::onBluetoothInfoReceived);
        for (IntentFilter intentFilter : BluetoothInfoReceiver.DEFAULT_FILTERS) {
            // note: needs to be RECEIVER_EXPORTED for scan mode change to be broadcast, not sure why
            getApplicationContext().registerReceiver(infoReceiver, intentFilter, RECEIVER_EXPORTED);
        }

        // register message receiver
        msgReceiver = new BluetoothMessageReceiver(BluetoothMessageParser.ofDefault(), this::onMsgReceived);
        getApplicationContext().registerReceiver(msgReceiver, new IntentFilter(BluetoothMessageReceiver.ACTION_MSG_READ), RECEIVER_NOT_EXPORTED);

        LocationManager locationManager = (LocationManager) getSystemService(Context.LOCATION_SERVICE);
        boolean isGpsEnabled = locationManager.isProviderEnabled(LocationManager.GPS_PROVIDER);
        if (!isGpsEnabled) {
            Log.d(TAG, "GPS / Location is not on, won't be able to discover non-paired devices.");
            Toast.makeText(this,"Turn on Location to Scan for devices.", Toast.LENGTH_SHORT).show();
        }
    }

    private void bindUI() {
        // bind UI to methods
        RecyclerView recyclerView = findViewById(R.id.btDeviceList);
        recyclerView.setLayoutManager(new LinearLayoutManager(this));
        bluetoothDeviceAdapter = new BluetoothDeviceAdapter(this, new ArrayList<>(), device -> {
            Toast.makeText(this, "Connecting to " + device.name(), Toast.LENGTH_SHORT).show();
            myApp.btInterface().connectAsClient(device.btDevice());
        });
        recyclerView.setAdapter(bluetoothDeviceAdapter);
        findViewById(R.id.btnScan).setOnClickListener(view -> refreshDeviceList());
        findViewById(R.id.btnDiscover).setOnClickListener(view -> enableDeviceDiscovery());

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

        Button canvasButton = findViewById(R.id.btnTemp);
        canvasButton.setOnClickListener(view -> {
            startActivity(new Intent(this, CanvasActivity.class));
        });
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        getApplicationContext().unregisterReceiver(infoReceiver);
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
                // ensure bluetooth is enabled
                if (!myApp.btInterface().isBluetoothEnabled()) {
                    Toast.makeText(this, "This app requires Bluetooth to function.", Toast.LENGTH_SHORT).show();
                    Intent enableBtIntent = new Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE);
                    requestEnableBluetooth.launch(enableBtIntent);
                } else {
                    // permission all good, init bluetooth
                    startBluetooth();
                }
            } else {
                // ask user for permissions
                showPermissionDeniedDialog();
            }
        }
    }

    private void enableDeviceDiscovery() {
        Intent discoverableIntent = new Intent(BluetoothAdapter.ACTION_REQUEST_DISCOVERABLE);
        discoverableIntent.putExtra(BluetoothAdapter.EXTRA_DISCOVERABLE_DURATION, DISCOVERABLE_DURATION);
        requestDiscoverable.launch(discoverableIntent);
        myApp.btInterface().acceptIncomingConnection();
    }

    private void refreshDeviceList() {
        // refresh paired devices and scan for new
        bluetoothDeviceAdapter.initPairedDevices(myApp.btInterface().getBondedDevices());
        myApp.btInterface().scanForDevices();
    }


    // starts scanning / connecting to devices
    private void startBluetooth() {
        if (myApp.btInterface().isBluetoothEnabled()) {
            // add all paired devices to device list
            bluetoothDeviceAdapter.initPairedDevices(myApp.btInterface().getBondedDevices());
            // start scanning for devices
            // myApp.btInterface().scanForDevices();
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
    private void onBluetoothInfoReceived(Intent intent, String action) {
        Log.d(TAG, "Received action: " + action);
        if (action.equals(BluetoothDevice.ACTION_FOUND)) {
            // discovered a bluetooth device
            BluetoothDevice device = intent.getParcelableExtra(BluetoothDevice.EXTRA_DEVICE, BluetoothDevice.class);
            if (device != null) {
                String deviceName = device.getName();
                String deviceHardwareAddress = device.getAddress(); // MAC address
                Log.d(TAG, "Discovered " + deviceName + " (" + deviceHardwareAddress + ")");
                bluetoothDeviceAdapter.addDiscoveredDevice(device);
            }
        } else if (action.equals(BluetoothConnection.ACTION_CONNECTED)) {
            boolean connected = intent.getBooleanExtra(BluetoothConnection.EXTRA_CONNECTED, false);
            BluetoothDevice device = intent.getParcelableExtra(BluetoothConnection.EXTRA_DEVICE, BluetoothDevice.class);
            if (device != null) {
                Log.d(TAG, "Connected to " + device.getName() + ": " + connected);
                if (!connected) {
                    // let other device reconnect
                    // enableDeviceDiscovery();
                    // and also initiate reconnection
                    Toast.makeText(this, "Reconnecting to " + device.getName(), Toast.LENGTH_SHORT).show();
                    myApp.btInterface().connectAsClient(device);
                }
            }
        }
    }

    private void sendMessageToCanvas(String message) {
        Intent intent = new Intent("BluetoothMessageReceived");
        intent.putExtra("message", message);
        LocalBroadcastManager.getInstance(this).sendBroadcast(intent);
    }

    private void onMsgReceived(BluetoothMessage btMsg) {
        if (btMsg instanceof BluetoothMessage.PlainStringMessage m) {
            sendMessageToCanvas(m.rawMsg());
            receivedMsgView.append(m.rawMsg() + "\n");
        } else if (btMsg instanceof BluetoothMessage.RobotStatusMessage m) {
            sendMessageToCanvas(m.status());
            statusView.setText(m.status());
        } else if (btMsg instanceof BluetoothMessage.TargetFoundMessage m) {
            sendMessageToCanvas(m.rawMsg());
            receivedMsgView.append("image-rec! " + m.rawMsg() + "\n"); // just print on ui for now
        } else if (btMsg instanceof BluetoothMessage.RobotPositionMessage m) {
            sendMessageToCanvas(m.rawMsg());
            receivedMsgView.append("location! " + m.rawMsg() + "\n"); // just print on ui for now
        }
    }
}