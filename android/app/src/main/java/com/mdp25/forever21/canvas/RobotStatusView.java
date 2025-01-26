package com.mdp25.forever21.canvas;

import android.app.Activity;
import com.mdp25.forever21.bluetooth.BluetoothMessageParser;

/**
 * Uses {@link BluetoothMessageParser} to parse the status message and display on UI.
 */
public class RobotStatusView {
    private final Activity activity;
    public RobotStatusView(Activity activity) {
        this.activity = activity;
    }

}
