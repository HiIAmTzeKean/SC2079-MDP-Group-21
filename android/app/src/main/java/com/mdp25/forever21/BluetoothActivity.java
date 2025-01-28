package com.mdp25.forever21;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;

import android.Manifest;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Bundle;
import android.provider.Settings;
import android.widget.Toast;

import com.mdp25.forever21.bluetooth.BluetoothInterface;

public class BluetoothActivity extends AppCompatActivity {

    private BluetoothInterface bluetoothInterface;

    private static final int BLUETOOTH_PERMISSIONS_REQUEST_CODE = 96;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_bluetooth);

        // first request bluetooth permissions
        String[] permissions = new String[]{
                Manifest.permission.BLUETOOTH_SCAN,
                Manifest.permission.BLUETOOTH_CONNECT,
                Manifest.permission.BLUETOOTH_ADVERTISE
        };
        requestPermissions(permissions, BLUETOOTH_PERMISSIONS_REQUEST_CODE);
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
                initBluetooth();
            } else {
                // ask user for permissions
                showPermissionDeniedDialog();
            }
        }
    }

    // key function to set up bluetooth, check bluetoothInterface for impl
    private void initBluetooth() {
        bluetoothInterface = new BluetoothInterface(this);

        if (!bluetoothInterface.isBluetoothEnabled()) {
            Toast.makeText(this, "This app requires Bluetooth to function.", Toast.LENGTH_SHORT).show();
        }

        // concurrently accept any incoming bt connections,
        bluetoothInterface.acceptIncomingConnection();
        // while scanning for devices to connect to
        bluetoothInterface.scanForDevices();
    }

    private void showPermissionDeniedDialog() {
        new AlertDialog.Builder(this)
                .setTitle("Bluetooth Permissions Required")
                .setMessage("This app needs Bluetooth permissions to function properly. " +
                        "Please grant the permissions in Settings.")
                .setPositiveButton("Open Settings", new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialog, int which) {
                        Intent intent = new Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS);
                        intent.setData(Uri.fromParts("package", getPackageName(), null));
                        startActivity(intent);
                    }
                })
                .setNegativeButton("Cancel", null)
                .show();
    }
}