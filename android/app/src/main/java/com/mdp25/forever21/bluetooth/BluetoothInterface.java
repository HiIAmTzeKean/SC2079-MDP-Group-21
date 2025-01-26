package com.mdp25.forever21.bluetooth;

import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothSocket;
import java.io.InputStream;
import java.io.OutputStream;
import java.util.UUID;

/**
 * Class which creates bluetooth connections.
 * <p> For this project, this android app is always the master, and the robot shall be the slave.
 * <p> Note that this class is not responsbile for the lifetime management of
 * resulting {@link BluetoothConnection}
 */
public class BluetoothInterface {
    //TODO, likely can refer

    private static final UUID MY_UUID = UUID.fromString("00001101-0000-1000-8000-00805F9B34FB"); // standard SerialPortServiceClass UUID?
    private BluetoothSocket mmSocket;
    private InputStream mmInStream;
    private OutputStream mmOutStream;
    private BluetoothAdapter bluetoothAdapter;
}
