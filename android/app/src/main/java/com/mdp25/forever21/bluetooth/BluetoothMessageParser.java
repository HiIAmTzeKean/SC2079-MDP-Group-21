package com.mdp25.forever21.bluetooth;

import java.util.function.Function;

/**
 * Interface for a message parser. Has a default implementation {@link #ofDefault}.
 */
public interface BluetoothMessageParser extends Function<String, BluetoothMessage> {

    // note no error checking is done, assume message is valid
    // technically not a secure approach, but fine for this project

    BluetoothMessageParser DEFAULT = msg -> {
        String[] split = msg.split(",");
        if (split.length > 1) {
            String pattern = split[0];
            return switch (pattern) {
                case "STATUS" -> BluetoothMessage.ofRobotStatusMessage(msg, split[1]);
                case "TARGET" -> BluetoothMessage.ofTargetFoundMessage(msg, Integer.parseInt(split[1]), Integer.parseInt(split[2]));
                case "ROBOT" -> BluetoothMessage.ofRobotPositionMessage(msg, Integer.parseInt(split[1]), Integer.parseInt(split[2]), Integer.parseInt(split[3])); //TODO
                default -> BluetoothMessage.ofPlainStringMessage(msg);
            };
        }
        return BluetoothMessage.ofPlainStringMessage(msg);
    };

    public static BluetoothMessageParser ofDefault() {
        return DEFAULT;
    }
}
