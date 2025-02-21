package com.mdp25.forever21;

import android.app.Application;

import com.mdp25.forever21.bluetooth.BluetoothConnection;
import com.mdp25.forever21.bluetooth.BluetoothInterface;

/**
 * Application class to hold app-scoped variables, such as the bluetooth connection handler.
 */
public class MyApplication extends Application {
    private BluetoothInterface bluetoothInterface;

    @Override
    public void onCreate() {
        super.onCreate();
        bluetoothInterface = new BluetoothInterface(this);
    }

    //getters omit "get" to showcase immutability, liken to records
    public BluetoothInterface btInterface() {
        return bluetoothInterface;
    }

    public BluetoothConnection btConnection() {
        return bluetoothInterface.getBluetoothConnection();
    }
}