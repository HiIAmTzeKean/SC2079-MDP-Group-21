package com.mdp25.forever21;

import androidx.appcompat.app.AppCompatActivity;

import android.os.Bundle;
import android.widget.ScrollView;
import android.widget.TextView;

import com.mdp25.forever21.canvas.CanvasGestureController;
import com.mdp25.forever21.canvas.CanvasTouchController;
import com.mdp25.forever21.canvas.CanvasView;
import com.mdp25.forever21.canvas.Grid;

/**
 * Main screen, displays the grid canvas and various controls.
 */
public class CanvasActivity extends AppCompatActivity {
    private TextView receivedMessages;
    private ScrollView scrollReceivedMessages;
    private final String TAG = "CanvasActivity";
    private MyApplication myApp; // my context for "static" var
    private CanvasView canvasView; // the "model-view" classes to define the UI
    private CanvasTouchController canvasTouchController; // the "controller" classes to perform interactions
    private CanvasGestureController canvasGestureController;
    private Grid grid;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_canvas);

        myApp = (MyApplication) getApplication();
        grid = new Grid();
        canvasView = findViewById(R.id.canvasView);
        canvasView.setGrid(grid);

        canvasTouchController = new CanvasTouchController(canvasView);
        canvasGestureController = new CanvasGestureController();

        bindUI(); // Call bindUI to set up buttons and interactions
    }



    private void bindUI() {
        // Bind robot movement buttons to Bluetooth commands
        findViewById(R.id.btnRobotForward).setOnClickListener(view -> myApp.btConnection().sendMessage("f"));
        findViewById(R.id.btnRobotBackward).setOnClickListener(view -> myApp.btConnection().sendMessage("r"));
        findViewById(R.id.btnRobotRight).setOnClickListener(view -> myApp.btConnection().sendMessage("tr"));
        findViewById(R.id.btnRobotLeft).setOnClickListener(view -> myApp.btConnection().sendMessage("tl"));
    }
}