package com.mdp25.forever21.bluetooth;

import android.util.Log;

import java.util.function.Function;

/**
 * Interface for a message parser. Has a default implementation {@link #ofDefault}.
 */
public interface BluetoothMessageParser extends Function<String, BluetoothMessage> {

    public static final String TAG = "BluetoothMessageParser";

    /**
     * Default message format is {@code "command;param1;param2" }.
     * <p> Expected messages:
     * <ul>
     *     <li>info</li>
     *     <li>error</li>
     *     <li>mode</li>
     *     <li>status</li>
     *     <li>location</li>
     *     <li>image-rec</li>
     * </ul>
     */
    BluetoothMessageParser DEFAULT = msg -> {
        String[] params = msg.split(";");
        if (params.length > 1) {
            String command = params[0];
            BluetoothMessage ret;
            switch (command) {
                case "info" -> ret = BluetoothMessage.ofPlainStringMessage("[info] " + params[1]);
                case "error" -> ret = BluetoothMessage.ofPlainStringMessage("[error] " + params[1]);
                case "mode" -> ret = BluetoothMessage.ofPlainStringMessage("[mode] " + params[1]);
                case "status" -> ret = BluetoothMessage.ofRobotStatusMessage(msg, params[1]);
                case "location" -> {
                    int[] intParams = tryGetIntParams(params, 3);
                    ret = BluetoothMessage.ofRobotPositionMessage(msg, intParams[0], intParams[1], intParams[2]);
                }
                case "image-rec" -> {
                    int[] intParams = tryGetIntParams(params, 2);
                    ret = BluetoothMessage.ofTargetFoundMessage(msg, intParams[0], intParams[1]);
                }
                default -> ret = BluetoothMessage.ofPlainStringMessage(msg);
            }
            ;
            return ret;
        }
        return BluetoothMessage.ofPlainStringMessage(msg);
    };

    public static int[] tryGetIntParams(String[] params, int expectedSize) {
        int[] ret = new int[expectedSize];
        // if input not valid just return empty list
        if (params.length <= expectedSize) {
            Log.e(TAG, String.format("Error in params, expected %d but size was %d", expectedSize, params.length));
            return ret;
        }
        // start from params index 1, since 0 is command
        for (int i = 0; i < expectedSize; ++i) {
            try {
                ret[i] = Integer.parseInt(params[i + 1].trim());
            } catch (NumberFormatException e) {
                ret[i] = 0; //put a safe non-crash value
                Log.e(TAG, "Error in parsing " + params[i + 1]);
            }
        }
        return ret;
    }

    public static BluetoothMessageParser ofDefault() {
        return DEFAULT;
    }
}
