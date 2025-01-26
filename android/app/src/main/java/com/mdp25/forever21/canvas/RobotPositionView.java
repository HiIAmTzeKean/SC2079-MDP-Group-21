package com.mdp25.forever21.canvas;

import android.app.Activity;

import com.mdp25.forever21.bluetooth.RobotBluetoothComm;

/**
 * Displays the robot position on screen (data observed from {@link RobotBluetoothComm}).
 * TODO handles interpolation / animation.
 */
public class RobotPositionView {
    private final Activity activity;
    public RobotPositionView(Activity activity) {
        this.activity = activity;
    }
}
