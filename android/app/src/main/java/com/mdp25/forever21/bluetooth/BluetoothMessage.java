package com.mdp25.forever21.bluetooth;

import android.bluetooth.BluetoothDevice;
import android.content.Intent;
import android.os.Parcel;
import android.os.Parcelable;

import androidx.annotation.NonNull;

import java.util.Objects;

/**
 * Represents a bluetooth message sent FROM the robot.
 * <p> Essentially wraps around a raw message string and provides the parsed info as getters.
 * <p> Use {@code ofXXX()} to create the subclassed record.
 */
public sealed interface BluetoothMessage permits BluetoothMessage.CustomMessage, BluetoothMessage.PlainStringMessage, BluetoothMessage.RobotPositionMessage, BluetoothMessage.RobotStatusMessage, BluetoothMessage.TargetFoundMessage {
    // this class uses the sealed..permit feature as a usage example, not strictly necessary

    public record RobotStatusMessage(String rawMsg, String status) implements BluetoothMessage {}
    public static BluetoothMessage ofRobotStatusMessage(String rawMsg, String status) {
        return new RobotStatusMessage(rawMsg, status);
    }

    public record TargetFoundMessage(String rawMsg, int obstacleId, int targetId) implements BluetoothMessage {}
    public static BluetoothMessage ofTargetFoundMessage(String rawMsg, int obstacleId, int targetId) {
        return new TargetFoundMessage(rawMsg, obstacleId, targetId);
    }

    public record RobotPositionMessage(String rawMsg, int x, int y, int direction) implements BluetoothMessage {}
    public static BluetoothMessage ofRobotPositionMessage(String rawMsg, int x, int y, int direction) {
        return new RobotPositionMessage(rawMsg, x, y, direction);
    }

    public record PlainStringMessage(String rawMsg) implements BluetoothMessage {}
    public static BluetoothMessage ofPlainStringMessage(String rawMsg) {
        return new PlainStringMessage(rawMsg);
    }

    /**
     * This non-sealed class is provided for future extension.
     */
    public abstract non-sealed class CustomMessage implements BluetoothMessage {}

}
