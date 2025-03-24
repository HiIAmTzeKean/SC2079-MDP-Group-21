package com.mdp25.forever21;

import android.app.Application;

import com.mdp25.forever21.bluetooth.BluetoothConnection;
import com.mdp25.forever21.bluetooth.BluetoothInterface;
import com.mdp25.forever21.canvas.Grid;
import com.mdp25.forever21.canvas.Robot;

/**
 * Application class to hold app-scoped variables, such as the bluetooth connection handler.
 */
public class MyApplication extends Application {
    private BluetoothInterface bluetoothInterface;
    private Grid grid;
    private Robot robot;

    @Override
    public void onCreate() {
        super.onCreate();
        bluetoothInterface = new BluetoothInterface(this);
        grid = new Grid();
        robot = Robot.ofDefault();
    }

    //getters omit "get" to showcase immutability, liken to records
    public BluetoothInterface btInterface() {
        return bluetoothInterface;
    }

    public BluetoothConnection btConnection() {
        return bluetoothInterface.getBluetoothConnection();
    }

    public Grid grid() {
        return grid;
    }

    public Robot robot() {
        return robot;
    }
}