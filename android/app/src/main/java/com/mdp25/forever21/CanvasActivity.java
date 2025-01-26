package com.mdp25.forever21;

import androidx.appcompat.app.AppCompatActivity;

import android.os.Bundle;

import com.mdp25.forever21.canvas.CanvasGestureController;
import com.mdp25.forever21.canvas.CanvasTouchController;
import com.mdp25.forever21.canvas.CanvasView;
import com.mdp25.forever21.canvas.RobotController;
import com.mdp25.forever21.canvas.RobotPositionView;
import com.mdp25.forever21.canvas.RobotStatusView;

/**
 * Main screen, displays the grid canvas and various controls.
 */
public class CanvasActivity extends AppCompatActivity {

    private final String TAG = "CanvasActivity";

    private AppContext appContext;


    // the "model-view" classes to define the UI:
    private CanvasView canvasView;
    private RobotPositionView robotPosView;
    private RobotStatusView robotStatusView;

    // the "controller" classes to perform interactions:
    private CanvasTouchController canvasTouchController;
    private CanvasGestureController canvasGestureController;
    private RobotController robotController;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_canvas);

        //TODO get app context from args
        appContext = InitActivity.getAppContext();

        canvasView = new CanvasView(this);
        robotPosView = new RobotPositionView(this);
        robotStatusView = new RobotStatusView(this);

        canvasTouchController = new CanvasTouchController();
        canvasGestureController = new CanvasGestureController();
        robotController = new RobotController();
    }
}