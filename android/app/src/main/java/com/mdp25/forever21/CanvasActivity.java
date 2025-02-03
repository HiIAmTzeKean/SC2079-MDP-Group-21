package com.mdp25.forever21;

import androidx.appcompat.app.AppCompatActivity;

import android.os.Bundle;

import com.mdp25.forever21.canvas.CanvasGestureController;
import com.mdp25.forever21.canvas.CanvasTouchController;
import com.mdp25.forever21.canvas.CanvasView;

/**
 * Main screen, displays the grid canvas and various controls.
 */
public class CanvasActivity extends AppCompatActivity {

    private final String TAG = "CanvasActivity";


    private MyApplication myApp; // my context for "static" vars


    // the "model-view" classes to define the UI:
    private CanvasView canvasView;

    // the "controller" classes to perform interactions:
    private CanvasTouchController canvasTouchController;
    private CanvasGestureController canvasGestureController;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_canvas);

        myApp = (MyApplication) getApplication();

        canvasView = new CanvasView(this);

        canvasTouchController = new CanvasTouchController();
        canvasGestureController = new CanvasGestureController();
    }
}