package com.mdp25.forever21;

import androidx.appcompat.app.AppCompatActivity;

import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.View;
import android.widget.ScrollView;
import android.widget.TextView;

import com.mdp25.forever21.canvas.CanvasGestureController;
import com.mdp25.forever21.canvas.CanvasTouchController;
import com.mdp25.forever21.canvas.CanvasView;

/**
 * Main screen, displays the grid canvas and various controls.
 */
public class CanvasActivity extends AppCompatActivity {
    private TextView receivedMessages;
    private ScrollView scrollReceivedMessages;
    private final Handler handler = new Handler(Looper.getMainLooper());
    private final String TAG = "CanvasActivity";
    private MyApplication myApp; // my context for "static" var
    private CanvasView canvasView; // the "model-view" classes to define the UI
    private CanvasTouchController canvasTouchController; // the "controller" classes to perform interactions
    private CanvasGestureController canvasGestureController;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_canvas);

        myApp = (MyApplication) getApplication();

        canvasView = new CanvasView(this);
        canvasTouchController = new CanvasTouchController();
        canvasGestureController = new CanvasGestureController();

        bindUI(); // Call bindUI to set up buttons and interactions
    }

    private void bindUI() {
        // Bind robot movement buttons to Bluetooth commands
        findViewById(R.id.btnRobotForward).setOnClickListener(view -> myApp.btConnection().sendMessage("f"));
        findViewById(R.id.btnRobotBackward).setOnClickListener(view -> myApp.btConnection().sendMessage("r"));
        findViewById(R.id.btnRobotRight).setOnClickListener(view -> myApp.btConnection().sendMessage("tr"));
        findViewById(R.id.btnRobotLeft).setOnClickListener(view -> myApp.btConnection().sendMessage("tl"));

        receivedMessages = findViewById(R.id.receivedMessages);
        scrollReceivedMessages = findViewById(R.id.scrollReceivedMessages);
    }

    public void receiveBluetoothMessage(String message) {
        runOnUiThread(() -> {
            receivedMessages.append("\n" + message);
            scrollReceivedMessages.post(() -> scrollReceivedMessages.fullScroll(View.FOCUS_DOWN));
        });
    }

}