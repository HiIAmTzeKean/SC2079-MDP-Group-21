package com.mdp25.forever21.bluetooth;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.util.Log;

import java.util.Objects;
import java.util.function.Consumer;

/**
 * Class used to listen to bluetooth messages "globally".
 * <p> The receiver should be registered on the application's context.
 */
public class BluetoothMessageReceiver extends BroadcastReceiver {

    private BluetoothMessageParser parser;
    private Consumer<BluetoothMessage> msgConsumer;
    public BluetoothMessageReceiver(BluetoothMessageParser parser, Consumer<BluetoothMessage> msgConsumer) {
        this.parser = parser;
        this.msgConsumer = msgConsumer;
    }
    private final static String TAG = "BluetoothMessageReceiver";
    public final static String ACTION_MSG_READ = BluetoothConnection.ACTION_MSG_READ; // defined for convenience
    public final static String EXTRA_MSG_READ = BluetoothConnection.EXTRA_MSG_READ; // defined for convenience
    @Override
    public void onReceive(Context context, Intent intent) {
        if (!Objects.equals(intent.getAction(), ACTION_MSG_READ)) {
            return;
        }
        String msg = intent.getStringExtra(EXTRA_MSG_READ);
        Log.d(TAG, "Received msg: " + msg);
        BluetoothMessage btMsg = parser.apply(msg);
        Log.d(TAG, "Parsed msg: " + btMsg);
        msgConsumer.accept(btMsg);
    }
}
