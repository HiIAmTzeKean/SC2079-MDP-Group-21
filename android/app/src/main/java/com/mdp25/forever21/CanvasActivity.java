package com.mdp25.forever21;

import androidx.appcompat.app.AppCompatActivity;
import androidx.localbroadcastmanager.content.LocalBroadcastManager;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.os.Bundle;
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

        canvasView = findViewById(R.id.canvasView);
        canvasTouchController = new CanvasTouchController(canvasView);
        canvasGestureController = new CanvasGestureController();

        bindUI(); // Call bindUI to set up buttons and interactions

        // Register the broadcast receiver
        LocalBroadcastManager.getInstance(this).registerReceiver(bluetoothReceiver, new IntentFilter("BluetoothMessageReceived"));
    }

    private final BroadcastReceiver bluetoothReceiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            String message = intent.getStringExtra("message");
            if (message != null) {
                receiveBluetoothMessage(message); // Update the UI
            }
        }
    };

    @Override
    protected void onDestroy() {
        super.onDestroy();
        unregisterReceiver(bluetoothReceiver);
    }

    public void receiveBluetoothMessage(String message) {
        runOnUiThread(() -> {
            receivedMessages.append("\n" + message);
            scrollReceivedMessages.post(() -> scrollReceivedMessages.fullScroll(View.FOCUS_DOWN));
        });
    }

    private void bindUI() {
        // Bind robot movement buttons to Bluetooth commands
        findViewById(R.id.btnRobotForward).setOnClickListener(view -> myApp.btConnection().sendMessage("f"));
        findViewById(R.id.btnRobotBackward).setOnClickListener(view -> myApp.btConnection().sendMessage("r"));
        findViewById(R.id.btnRobotRight).setOnClickListener(view -> myApp.btConnection().sendMessage("tr"));
        findViewById(R.id.btnRobotLeft).setOnClickListener(view -> myApp.btConnection().sendMessage("tl"));

        receivedMessages = findViewById(R.id.receivedMessagesDynamic);
        scrollReceivedMessages = findViewById(R.id.scrollReceivedMessages);
    }
}