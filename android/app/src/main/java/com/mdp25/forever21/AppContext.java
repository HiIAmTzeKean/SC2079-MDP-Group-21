package com.mdp25.forever21;

import com.mdp25.forever21.bluetooth.RobotBluetoothComm;

/**
 * This object lasts the entire app lifetime, and stores contextual info,
 * such as a reference to the robot's {@link RobotBluetoothComm}.
 */
public class AppContext {
    private static boolean created = false;
    public AppContext() {
        if (created)
            throw new RuntimeException("Duplicate AppContext, is this intentional?");
        created = true;
    }
}
