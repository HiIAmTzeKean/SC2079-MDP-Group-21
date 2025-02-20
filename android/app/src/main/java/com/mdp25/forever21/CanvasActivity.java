package com.mdp25.forever21;

import androidx.appcompat.app.AppCompatActivity;

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
import com.mdp25.forever21.canvas.CanvasGestureController;
import com.mdp25.forever21.canvas.CanvasTouchController;
import com.mdp25.forever21.canvas.CanvasView;
import com.mdp25.forever21.canvas.Grid;
import com.mdp25.forever21.canvas.Robot;
import com.mdp25.forever21.canvas.RobotView;

public class CanvasActivity extends AppCompatActivity {
    private TextView receivedMessages;
    private TextView robotStatusDynamic;
    private ScrollView scrollReceivedMessages;
    private Spinner spinnerRobotFacing;
    private Button btnInitializeRobot;
    private Button sendbtn;
    private Button startbtn;
    private EditText inputX;
    private EditText inputY;
    private EditText chatInputBox;
    private String selectedFacing = "NORTH"; // Default value
    private Facing facingDirection;
    private final String TAG = "CanvasActivity";
    private MyApplication myApp;
    private CanvasView canvasView;
    private RobotView robotView;
    private CanvasTouchController canvasTouchController;
    private CanvasGestureController canvasGestureController;
    private Grid grid;
    private Robot robot;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_canvas);

        myApp = (MyApplication) getApplication();
        grid = new Grid();
        robot = Robot.of(1, 1, Facing.NORTH); // Initialize robot

        canvasTouchController = new CanvasTouchController(grid);
        canvasGestureController = new CanvasGestureController();

        canvasView = findViewById(R.id.canvasView);
        canvasView.setGrid(grid);
        canvasView.setOnTouchListener(canvasTouchController);

        robotView = findViewById(R.id.robotView);
        robotView.setRobot(robot);

        bindUI(); // Calls method to initialize UI components
    }

    private void bindUI() {
        // Initialize input fields
        inputX = findViewById(R.id.inputX);
        inputY = findViewById(R.id.inputY);
        applyInputFilter(inputX);
        applyInputFilter(inputY);
        chatInputBox = findViewById(R.id.chatInputBox);
        // TODO Bluetooth stuff
        receivedMessages = findViewById(R.id.ReceiveMsgTextView);
        robotStatusDynamic = findViewById(R.id.robotStatusDynamic);

        // Initialize scroll view
        scrollReceivedMessages = findViewById(R.id.ReceiveMsgScrollView);

        // Initialize spinner
        spinnerRobotFacing = findViewById(R.id.spinnerRobotFacing);
        setupSpinner();

        // Initialize buttons
        btnInitializeRobot = findViewById(R.id.btnInitializeRobot);
        btnInitializeRobot.setOnClickListener(view -> initializeRobotFromInput());
        sendbtn = findViewById(R.id.btnSend);
        sendbtn.setOnClickListener(view -> sendChatMessage());
        startbtn = findViewById(R.id.btnRobotStart);
        startbtn.setOnClickListener(view -> startRobot());

        // Bind movement buttons
        findViewById(R.id.btnRobotForward).setOnClickListener(view -> {
            myApp.btConnection().sendMessage("f");
            robot.moveForward();
            robotView.invalidate();
        });
        findViewById(R.id.btnRobotBackward).setOnClickListener(view -> {
            myApp.btConnection().sendMessage("r");
            robot.moveBackward();
            robotView.invalidate();
        });
        findViewById(R.id.btnRobotRight).setOnClickListener(view -> {
            myApp.btConnection().sendMessage("tr");
            robot.turnRight();
            robotView.invalidate();
        });
        findViewById(R.id.btnRobotLeft).setOnClickListener(view -> {
            myApp.btConnection().sendMessage("tl");
            robot.turnLeft();
            robotView.invalidate();
        });
    }

    private void startRobot() {
        BluetoothMessage msg = BluetoothMessage.ofObstaclesMessage(this.robot.getPosition(),
                this.robot.getFacing(),
                this.grid.getObstacleList());
        myApp.btConnection().sendMessage(msg.getAsJsonMessage().getAsJson());
        msg = BluetoothMessage.ofRobotStartMessage();
        myApp.btConnection().sendMessage(msg.getAsJsonMessage().getAsJson());
    }

    private void applyInputFilter(EditText input) {
        InputFilter minMaxFilter = new InputFilter() {
            @Override
            public CharSequence filter(CharSequence source, int start, int end, Spanned dest, int dstart, int dend) {
                try {
                    int inputVal = Integer.parseInt(dest.toString() + source.toString());
                    if (inputVal >= 0 && inputVal <= 19) return null;
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
            public void onNothingSelected(AdapterView<?> parent) {}
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
        robot.updatePosition(x, y);
        robot.updateFacing(facing);
        robotView.invalidate();
    }

    private Facing convertFacing(String facing) {
        switch (facing.toUpperCase()) {
            case "NORTH": return Facing.NORTH;
            case "SOUTH": return Facing.SOUTH;
            case "EAST": return Facing.EAST;
            case "WEST": return Facing.WEST;
            default: return Facing.NORTH;
        }
    }
}