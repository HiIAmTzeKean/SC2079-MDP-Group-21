package com.mdp25.forever21.bluetooth;

import android.util.Log;

import com.mdp25.forever21.canvas.GridObstacle;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.List;

/**
 * Represents a bluetooth message sent FROM the robot.
 * <p> Essentially wraps around a raw message string and provides the parsed info as getters.
 * <p> Use {@code ofXXX()} to create the subclassed record.
 */
public sealed interface BluetoothMessage permits BluetoothMessage.CustomMessage, BluetoothMessage.ObstaclesMessage, BluetoothMessage.PlainStringMessage, BluetoothMessage.RobotMoveMessage, BluetoothMessage.RobotPositionMessage, BluetoothMessage.RobotStartMessage, BluetoothMessage.RobotStatusMessage, BluetoothMessage.TargetFoundMessage {
    // this class uses the sealed..permit feature as a usage example, not strictly necessary

    public static final String TAG = "BluetoothMessage";

    /**
     * Received from RPI.
     */
    public record RobotStatusMessage(String rawMsg, String status) implements BluetoothMessage {}
    public static BluetoothMessage ofRobotStatusMessage(String rawMsg, String status) {
        return new RobotStatusMessage(rawMsg, status);
    }

    /**
     * Received from RPI.
     */
    public record TargetFoundMessage(String rawMsg, int obstacleId, int targetId) implements BluetoothMessage {}
    public static BluetoothMessage ofTargetFoundMessage(String rawMsg, int obstacleId, int targetId) {
        return new TargetFoundMessage(rawMsg, obstacleId, targetId);
    }

    /**
     * Received from RPI.
     */
    public record RobotPositionMessage(String rawMsg, int x, int y, int direction) implements BluetoothMessage {}
    public static BluetoothMessage ofRobotPositionMessage(String rawMsg, int x, int y, int direction) {
        return new RobotPositionMessage(rawMsg, x, y, direction);
    }

    /**
     * Any plain old string message from RPI.
     */
    public record PlainStringMessage(String rawMsg) implements BluetoothMessage {}
    public static BluetoothMessage ofPlainStringMessage(String rawMsg) {
        return new PlainStringMessage(rawMsg);
    }

    /**
     * Sent to RPI.
     */
    public record RobotMoveMessage(RobotMoveCommand cmd) implements BluetoothMessage, JsonMessage {
        @Override
        public String getAsJson() {
            return getFormatted("control", cmd.value());
        }
    }
    public static BluetoothMessage ofRobotMoveMessage(RobotMoveCommand cmd) {
        return new RobotMoveMessage(cmd);
    }

    /**
     * Sent to RPI.
     */
    public record RobotStartMessage() implements BluetoothMessage, JsonMessage {
        @Override
        public String getAsJson() {
            return getFormatted("control", "start");
        }
    }
    public static BluetoothMessage ofRobotStartMessage() {
        return new RobotStartMessage();
    }

    /**
     * Sent to RPI.
     * TODO
     */
    public record ObstaclesMessage(List<GridObstacle> obstacleList) implements BluetoothMessage, JsonMessage {
        @Override
        public String getAsJson() {
            JSONObject jsonObject = new JSONObject();
            try {
                jsonObject.put("mode", "0");
                JSONArray arr = new JSONArray();
                for (GridObstacle obst : obstacleList) {
                    JSONObject obstJson = new JSONObject();
//                    obstJson.put("x", obst.); // TODO waiting on obstacles class...
//                    obstJson.put("y", obst.);
//                    obstJson.put("id", obst.);
//                    obstJson.put("d", obst.);
                    arr.put(obstJson);
                }
                jsonObject.put("obstacles", arr);
            } catch (JSONException e) {
                Log.e(TAG,"Error creating json for ObstaclesMessage");
                throw new RuntimeException(e);
            }
            return getFormatted("obstacles", jsonObject.toString());
        }
    }
    public static BluetoothMessage ofObstaclesMessage(List<GridObstacle> obstacleList) {
        return new ObstaclesMessage(obstacleList);
    }

    /**
     * This non-sealed class is provided for future extension.
     */
    public abstract non-sealed class CustomMessage implements BluetoothMessage {}

}
