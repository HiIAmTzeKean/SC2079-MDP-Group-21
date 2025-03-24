package com.mdp25.forever21.bluetooth;

import android.util.Log;

import com.mdp25.forever21.Facing;
import com.mdp25.forever21.Position;
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
     * Provided for convenience. Use cautiously, this is an unchecked cast.
     * @return possibly null
     */
    default public JsonMessage getAsJsonMessage() {
        if (this instanceof JsonMessage)
            return (JsonMessage) this;
        return null;
    }

    /**
     * Received from RPI
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
            return getFormattedStr("manual", cmd.value());
        }
    }
    public static BluetoothMessage ofRobotMoveMessage(RobotMoveCommand cmd) {
        return new RobotMoveMessage(cmd);
    }

    /**
     * Sent to RPI. Tells the robot to start moving (Task 1)
     */
    public record RobotStartMessage() implements BluetoothMessage, JsonMessage {
        @Override
        public String getAsJson() {
            return getFormattedStr("control", "start");
        }
    }
    public static BluetoothMessage ofRobotStartMessage() {
        return new RobotStartMessage();
    }

    /**
     * Sent to RPI. Sends robot the obstacle list and initial robot pos
     */
    public record ObstaclesMessage(Position robotInitPos, Facing robotInitDir, List<GridObstacle> obstacleList) implements BluetoothMessage, JsonMessage {
        @Override
        public String getAsJson() {
            JSONObject jsonObject = new JSONObject();
            try {
                jsonObject.put("robot_x", robotInitPos.getXInt());
                jsonObject.put("robot_y", robotInitPos.getYInt());
                jsonObject.put("robot_dir", robotInitDir.getMappedCode());
                jsonObject.put("mode", "0");
                JSONArray arr = new JSONArray();
                for (GridObstacle obst : obstacleList) {
                    JSONObject obstJson = new JSONObject();
                    obstJson.put("x", obst.getPosition().getXInt());
                    obstJson.put("y", obst.getPosition().getYInt());
                    obstJson.put("id", obst.getId());
                    obstJson.put("d", obst.getFacing().getMappedCode());
                    arr.put(obstJson);
                }
                jsonObject.put("obstacles", arr);
            } catch (JSONException e) {
                Log.e(TAG,"Error creating json for ObstaclesMessage");
                throw new RuntimeException(e);
            }
            return getFormattedObj("obstacles", jsonObject);
        }
    }
    public static BluetoothMessage ofObstaclesMessage(Position robotInitPos, Facing robotInitDir, List<GridObstacle> obstacleList) {
        return new ObstaclesMessage(robotInitPos, robotInitDir, obstacleList);
    }

    /**
     * This non-sealed class is provided for future extension.
     */
    public abstract non-sealed class CustomMessage implements BluetoothMessage {}

}
