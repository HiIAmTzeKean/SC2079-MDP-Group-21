package com.mdp25.forever21;

import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.annotation.NonNull;
import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;
import androidx.localbroadcastmanager.content.LocalBroadcastManager;
import androidx.recyclerview.widget.RecyclerView;

import android.Manifest;
import android.annotation.SuppressLint;
import android.app.Activity;
import android.bluetooth.BluetoothAdapter;
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
import com.mdp25.forever21.bluetooth.BluetoothInterface;
import com.mdp25.forever21.bluetooth.BluetoothMessage;
import com.mdp25.forever21.bluetooth.BluetoothMessageParser;

import java.util.Objects;

public class BluetoothActivity extends AppCompatActivity {

    private static final String TAG = "BluetoothActivity";
    private static final int BLUETOOTH_PERMISSIONS_REQUEST_CODE = 96;
    private static final int DISCOVERABLE_DURATION = 300;
    private BluetoothInterface bluetoothInterface;
    private BluetoothMessageParser parser;

    // UI variables below
    private RecyclerView recyclerView;
    private TextView receivedMsgView;
    private TextView statusView;
    private TextInputEditText msgInput;

    @SuppressLint("UnspecifiedRegisterReceiverFlag")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_bluetooth);

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
        enableDeviceDiscovery(DISCOVERABLE_DURATION);

        // register broadcast receivers
        BroadcastReceiver receiver = bluetoothInterface.getBroadcastReceiver();
        for (IntentFilter intentFilter : bluetoothInterface.getIntentFilters()) {
            registerReceiver(receiver, intentFilter);
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
        recyclerView.findViewById(R.id.btDeviceList);
        findViewById(R.id.btnScan).setOnClickListener(view -> bluetoothInterface.scanForDevices());
        // TODO findViewById(R.id.btnConnect).setOnClickListener(view -> bluetoothInterface.connectAsClient());

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