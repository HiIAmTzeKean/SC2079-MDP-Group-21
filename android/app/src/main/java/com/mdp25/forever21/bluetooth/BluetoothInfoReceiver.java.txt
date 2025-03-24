package com.mdp25.forever21.bluetooth;

import android.annotation.SuppressLint;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.util.Log;
import android.widget.Toast;

import java.util.function.BiConsumer;

public class BluetoothInfoReceiver extends BroadcastReceiver {


    private static final String TAG = "BluetoothInfoReceiver";
    private final BiConsumer<Intent, String> consumer;
    public static final IntentFilter[] DEFAULT_FILTERS = new IntentFilter[]{
            new IntentFilter(BluetoothAdapter.ACTION_SCAN_MODE_CHANGED), //scan on/off
            new IntentFilter(BluetoothAdapter.ACTION_STATE_CHANGED), // bt on/off
            new IntentFilter(BluetoothDevice.ACTION_FOUND), //discovered a device
            new IntentFilter(BluetoothDevice.ACTION_BOND_STATE_CHANGED), // paired/unpaired
            new IntentFilter(BluetoothConnection.ACTION_CONNECTED), // connected/disconnected
    };

    public BluetoothInfoReceiver(BiConsumer<Intent, String> consumer) {
        this.consumer = consumer;
    }

    @SuppressLint("MissingPermission")
    @Override
    public void onReceive(Context context, Intent intent) {
        Log.d(TAG, "Received broadcast: " + intent.getAction());
        String action = intent.getAction();
        if (action == null)
            return;
        switch (action) {
            case BluetoothAdapter.ACTION_SCAN_MODE_CHANGED -> {
                int mode = intent.getIntExtra(BluetoothAdapter.EXTRA_SCAN_MODE, BluetoothAdapter.ERROR);
                switch (mode) {
                    case BluetoothAdapter.SCAN_MODE_CONNECTABLE_DISCOVERABLE ->
                            Toast.makeText(context, "Discoverability is on", Toast.LENGTH_LONG).show();
                    case BluetoothAdapter.SCAN_MODE_CONNECTABLE, BluetoothAdapter.SCAN_MODE_NONE ->
                            Toast.makeText(context, "Discoverability is now off", Toast.LENGTH_LONG).show();
                }
            }
            case BluetoothAdapter.ACTION_STATE_CHANGED -> {
                int state = intent.getIntExtra(BluetoothAdapter.EXTRA_STATE, BluetoothAdapter.ERROR);
                switch (state) {
                    case BluetoothAdapter.STATE_OFF -> {
                        Toast.makeText(context, "Bluetooth is off", Toast.LENGTH_SHORT).show();
                        Toast.makeText(context, "This app requires Bluetooth to function", Toast.LENGTH_SHORT).show();
                    }
                    case BluetoothAdapter.STATE_ON ->
                            Toast.makeText(context, "Bluetooth is on", Toast.LENGTH_SHORT).show();
                }
            }
            case BluetoothDevice.ACTION_BOND_STATE_CHANGED -> {
                BluetoothDevice device = intent.getParcelableExtra(BluetoothDevice.EXTRA_DEVICE, BluetoothDevice.class);
                if (device != null) {
                    switch (device.getBondState()) {
                        case BluetoothDevice.BOND_NONE -> {
                            Toast.makeText(context, String.format("Unpaired with %s", device.getName()), Toast.LENGTH_SHORT).show();
                        }
                        case BluetoothDevice.BOND_BONDED ->
                                Toast.makeText(context, String.format("Paired to %s", device.getName()), Toast.LENGTH_SHORT).show();
                        case BluetoothDevice.BOND_BONDING ->
                                Toast.makeText(context, String.format("Pairing to %s", device.getName()), Toast.LENGTH_SHORT).show();

                    }
                }
            }
        }

        // does not fit into switch statement as it is not a "constant expression"
        if (action.equals(BluetoothConnection.ACTION_CONNECTED)) {
            boolean connected = intent.getBooleanExtra(BluetoothConnection.EXTRA_CONNECTED, false);
            BluetoothDevice device = intent.getParcelableExtra(BluetoothConnection.EXTRA_DEVICE, BluetoothDevice.class);
            if (device != null) {
                if (connected) {
                    Toast.makeText(context, "Connected to " + device.getName(), Toast.LENGTH_SHORT).show();
                } else {
                    Toast.makeText(context, "Disconnected from " + device.getName(), Toast.LENGTH_SHORT).show();
                }
            } else {
                Log.e(TAG, "Connected device is null?");
            }
        }

        consumer.accept(intent, action);
    }
}
