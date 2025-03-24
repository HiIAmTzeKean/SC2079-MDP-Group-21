package com.mdp25.forever21;

import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;

import android.content.BroadcastReceiver;
import android.content.IntentFilter;
import android.media.MediaPlayer;
import android.os.Bundle;
import android.widget.Button;
import android.widget.ScrollView;
import android.widget.TextView;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Spinner;
import android.widget.Toast;
import android.text.InputFilter;
import android.text.Spanned;
import android.widget.EditText;

import com.mdp25.forever21.bluetooth.BluetoothMessage;
import com.mdp25.forever21.bluetooth.BluetoothMessageParser;
import com.mdp25.forever21.bluetooth.BluetoothMessageReceiver;
import com.mdp25.forever21.canvas.CanvasTouchController;
import com.mdp25.forever21.canvas.CanvasView;
import com.mdp25.forever21.canvas.GridObstacle;
import com.mdp25.forever21.canvas.RobotView;


public class CanvasActivity extends AppCompatActivity {
    private TextView receivedMessages;
    private TextView robotStatusDynamic;
    private ScrollView scrollReceivedMessages;
    private Spinner spinnerRobotFacing;
    private Button btnInitializeRobot;
    private Button btnSendData;
    private Button sendbtn;
    private Button startbtn;
    private EditText inputX;
    private EditText inputY;
    private EditText chatInputBox;
    private String selectedFacing = "NORTH"; // Default value
    private Facing facingDirection;
    private final String TAG = "CanvasActivity";
    private MyApplication myApp;
    private BroadcastReceiver msgReceiver; //receive bluetooth messages
    private CanvasView canvasView;
    private RobotView robotView;
    private CanvasTouchController canvasTouchController;
    private MediaPlayer mediaPlayer;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_canvas);

        myApp = (MyApplication) getApplication();

        // reset robot pos and dir
        myApp.robot().updatePosition(1,1).updateFacing(Facing.NORTH);

        canvasTouchController = new CanvasTouchController(myApp);

        canvasView = findViewById(R.id.canvasView);
        canvasView.setGrid(myApp.grid());
        canvasView.setOnTouchListener(canvasTouchController);

        robotView = findViewById(R.id.robotView);
        robotView.setRobot(myApp.robot());

        bindUI(); // Calls method to initialize UI components

        msgReceiver = new BluetoothMessageReceiver(BluetoothMessageParser.ofDefault(), this::onMsgReceived);
        getApplicationContext().registerReceiver(msgReceiver, new IntentFilter(BluetoothMessageReceiver.ACTION_MSG_READ), RECEIVER_NOT_EXPORTED);
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (mediaPlayer != null) {
            mediaPlayer.release();
            mediaPlayer = null;
        }
    }

    private void bindUI() {
        // Initialize input fields
        inputX = findViewById(R.id.inputX);
        inputY = findViewById(R.id.inputY);
        applyInputFilter(inputX);
        applyInputFilter(inputY);
        inputX.setText(Integer.toString(myApp.robot().getPosition().getXInt()));
        inputY.setText(Integer.toString(myApp.robot().getPosition().getYInt()));
        chatInputBox = findViewById(R.id.chatInputBox);

        receivedMessages = findViewById(R.id.ReceiveMsgTextView);
        robotStatusDynamic = findViewById(R.id.robotStatusDynamic);

        // Initialize scroll view
        scrollReceivedMessages = findViewById(R.id.ReceiveMsgScrollView);

        // Initialize spinner
        spinnerRobotFacing = findViewById(R.id.spinnerRobotFacing);
        setupSpinner();

        // Initialize buttons
        btnSendData = findViewById(R.id.btnSendData);
        btnSendData.setOnClickListener(view -> sendData());
        btnInitializeRobot = findViewById(R.id.btnInitializeRobot);
        btnInitializeRobot.setOnClickListener(view -> initializeRobotFromInput());
        sendbtn = findViewById(R.id.btnSend);
        sendbtn.setOnClickListener(view -> sendChatMessage());
        startbtn = findViewById(R.id.btnRobotStart);
        startbtn.setOnClickListener(view -> {
            if (myApp.btConnection() != null) showConfirmationDialog();
        });

        // Bind movement buttons
//        findViewById(R.id.btnRobotForward).setOnClickListener(view -> {
//            if (myApp.btConnection() != null)
//                myApp.btConnection().sendMessage("f");
//            myApp.robot().moveForward();
//            robotView.invalidate();
//        });
//        findViewById(R.id.btnRobotBackward).setOnClickListener(view -> {
//            if (myApp.btConnection() != null)
//                myApp.btConnection().sendMessage("r");
//            myApp.robot().moveBackward();
//            robotView.invalidate();
//        });
//        findViewById(R.id.btnRobotRight).setOnClickListener(view -> {
//            if (myApp.btConnection() != null)
//                myApp.btConnection().sendMessage("tr");
//            myApp.robot().turnRight();
//            robotView.invalidate();
//        });
//        findViewById(R.id.btnRobotLeft).setOnClickListener(view -> {
//            if (myApp.btConnection() != null)
//                myApp.btConnection().sendMessage("tl");
//            myApp.robot().turnLeft();
//            robotView.invalidate();
//        });
    }

    private void startRobot() {
        BluetoothMessage msg = BluetoothMessage.ofRobotStartMessage();
        myApp.btConnection().sendMessage(msg.getAsJsonMessage().getAsJson());
        if (mediaPlayer != null) {
            mediaPlayer.stop();
            mediaPlayer.release();
        }
        mediaPlayer = MediaPlayer.create(this, R.raw.tokyo_drift);
        mediaPlayer.start();
        for (GridObstacle obstacle : myApp.grid().getObstacleList()) {
            obstacle.setTarget(null);
        }
        canvasView.invalidate();
    }

    private void showConfirmationDialog() {
        new AlertDialog.Builder(this)
                .setTitle("Confirm Start")
                .setMessage("Are you sure you want to start the robot?")
                .setPositiveButton("Confirm", (dialog, which) -> startRobot())
                .setNegativeButton("Cancel", (dialog, which) -> dialog.dismiss())
                .show();
    }

    private void sendData(){
        if (myApp.btConnection() == null) {
            Toast.makeText(CanvasActivity.this, "Error: No Bluetooth Connection", Toast.LENGTH_SHORT).show();
            return;
        }
        BluetoothMessage msg = BluetoothMessage.ofObstaclesMessage(myApp.robot().getPosition(),
                this.myApp.robot().getFacing(),
                this.myApp.grid().getObstacleList());
        myApp.btConnection().sendMessage(msg.getAsJsonMessage().getAsJson());
        Toast.makeText(CanvasActivity.this, "Data sent successfully", Toast.LENGTH_SHORT).show();
        if (mediaPlayer != null) {
            mediaPlayer.stop();
            mediaPlayer.release();
        }
        mediaPlayer = MediaPlayer.create(this, R.raw.elevator_music);
        mediaPlayer.start();
    }

    private void applyInputFilter(EditText input) {
        InputFilter minMaxFilter = new InputFilter() {
            @Override
            public CharSequence filter(CharSequence source, int start, int end, Spanned dest, int dstart, int dend) {
                try {
                    int inputVal = Integer.parseInt(dest.toString() + source.toString());
                    if (inputVal >= 1 && inputVal <= 3) return null;
                } catch (NumberFormatException e) {
                    return "";
                }
                return "";
            }
        };
        input.setFilters(new InputFilter[]{minMaxFilter});
    }

    private void setupSpinner() {
        ArrayAdapter<CharSequence> adapter = ArrayAdapter.createFromResource(
                this,
                R.array.robot_facing_options,
                android.R.layout.simple_spinner_item
        );
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        spinnerRobotFacing.setAdapter(adapter);
        spinnerRobotFacing.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
            @Override
            public void onItemSelected(AdapterView<?> parent, View view, int position, long id) {
                selectedFacing = parent.getItemAtPosition(position).toString();
                Toast.makeText(CanvasActivity.this, "Selected: " + selectedFacing, Toast.LENGTH_SHORT).show();
            }

            @Override
            public void onNothingSelected(AdapterView<?> parent) {
            }
        });
    }

    private void sendChatMessage() {
        String message = chatInputBox.getText().toString().trim();

        if (!message.isEmpty()) {
            myApp.btConnection().sendMessage(message); // Send the message via Bluetooth
            chatInputBox.setText(""); // Clear the input field after sending
            Toast.makeText(this, "Message sent: " + message, Toast.LENGTH_SHORT).show();
        } else {
            Toast.makeText(this, "Please enter a message", Toast.LENGTH_SHORT).show();
        }
    }

    private void initializeRobotFromInput() {
        if (inputX.getText().toString().isEmpty() || inputY.getText().toString().isEmpty()) {
            Toast.makeText(getApplicationContext(), "Please enter both X and Y values.", Toast.LENGTH_SHORT).show();
            return;
        }

        int x = Integer.parseInt(inputX.getText().toString());
        int y = Integer.parseInt(inputY.getText().toString());
        facingDirection = convertFacing(selectedFacing);

        initializeRobot(x, y, facingDirection);
    }

    private void initializeRobot(int x, int y, Facing facing) {
        myApp.robot().updatePosition(x, y);
        myApp.robot().updateFacing(facing);
        robotView.invalidate();
        if (mediaPlayer != null) {
            mediaPlayer.stop();
            mediaPlayer.release();
        }
        mediaPlayer = MediaPlayer.create(this, R.raw.hee_hee);
        mediaPlayer.start();
    }

    private Facing convertFacing(String facing) {
        switch (facing.toUpperCase()) {
            case "NORTH":
                return Facing.NORTH;
            case "SOUTH":
                return Facing.SOUTH;
            case "EAST":
                return Facing.EAST;
            case "WEST":
                return Facing.WEST;
            default:
                return Facing.NORTH;
        }
    }

    private void onMsgReceived(BluetoothMessage btMsg) {
        if (btMsg instanceof BluetoothMessage.PlainStringMessage m) {
            // show on ui
            receivedMessages.append("\n" + m.rawMsg() + "\n");
            if (m.rawMsg().equals("[info] Commands and path received Algo API. Robot is ready to move.")) {
                if (mediaPlayer != null) {
                    mediaPlayer.stop();
                    mediaPlayer.release();
                }
                mediaPlayer = MediaPlayer.create(this, R.raw.yippee);
                mediaPlayer.start();
            }
        } else if (btMsg instanceof BluetoothMessage.RobotStatusMessage m) {
            // show on ui
            robotStatusDynamic.setText(m.status().toUpperCase());
            receivedMessages.append("\n[status] " + m.rawMsg()+ "\n"); // just print on ui for now
            if (m.status().equals("finished")) {
                if (mediaPlayer != null) {
                    mediaPlayer.stop();
                    mediaPlayer.release();
                }
                mediaPlayer = MediaPlayer.create(this, R.raw.yippee);
                mediaPlayer.start();
            }
        } else if (btMsg instanceof BluetoothMessage.TargetFoundMessage m) {
            // update obstacle's target, then invalidate ui
            myApp.grid().updateObstacleTarget(m.obstacleId(), m.targetId());
            canvasView.invalidate();
            receivedMessages.append("\n[image-rec] " + m.rawMsg() + "\n"); // just print on ui for now
        } else if (btMsg instanceof BluetoothMessage.RobotPositionMessage m) {
            // update robot's pos, then invalidate ui
            myApp.robot().updatePosition(m.x(), m.y()).updateFacing(Facing.getFacingFromCode(m.direction()));
            robotView.invalidate();
            receivedMessages.append("\n[location] " + m.rawMsg() + "\n"); // just print on ui for now
        }
        scrollReceivedMessages.post(() -> scrollReceivedMessages.fullScroll(View.FOCUS_DOWN));
    }
}