package com.mdp25.forever21.bluetooth;

import android.bluetooth.BluetoothDevice;

/**
 * Simple entity class to represent a Bluetooth device with extra info.
 */
public record BluetoothDeviceModel(BluetoothDevice btDevice, String name, String address, boolean isPaired) {
}
