package com.mdp25.forever21.bluetooth;

/**
 * Interface for a message parser. Has a default implementation {@link #ofDefault}.
 */
public interface BluetoothMessageParser {
    public static BluetoothMessageParser ofDefault() {
        return new BluetoothMessageParser() {
            //TODO
        };
    }
}
