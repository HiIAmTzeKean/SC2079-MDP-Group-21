package com.mdp25.forever21.bluetooth;

/**
 * Represents a bluetooth message sent to/from the robot.
 * <p> Use {@code ofXXX()} to create the subclassed record.
 */
public sealed interface BluetoothMessage permits BluetoothMessage.CustomMessage, BluetoothMessage.StatusMessage {
    // this class uses the sealed..permit feature as a usage example, not strictly necessary

    //TODO, based on decided messages

    //TODO proper params
    public static BluetoothMessage ofStatusMessage() {
        return new StatusMessage("hi");
    }

    public static record StatusMessage(String msg) implements BluetoothMessage {}



    /**
     * This non-sealed class is provided for future extension.
     */
    public abstract non-sealed class CustomMessage implements BluetoothMessage {}

}
