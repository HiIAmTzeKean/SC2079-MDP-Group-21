package com.mdp25.forever21.canvas;

import android.content.Context;
import android.graphics.Rect;
import android.util.AttributeSet;
import android.view.View;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Canvas;

import com.mdp25.forever21.Facing;
import com.mdp25.forever21.R;


public class RobotView extends View {
    private static final String TAG = "RobotView";
    private Bitmap robotFacingNorth;
    private Bitmap robotFacingEast;
    private Bitmap robotFacingSouth;
    private Bitmap robotFacingWest;
    private int cellSize;  // Dynamically calculated
    private int offsetX, offsetY; // To align with the grid
    private Robot robot;

    public RobotView(Context context, AttributeSet attrs) {
        super(context, attrs);
        init();
    }

    private void init() {
        // Load the robot PNG from resources
        robotFacingNorth = BitmapFactory.decodeResource(getResources(), R.drawable.annie_face_up);
        robotFacingEast = BitmapFactory.decodeResource(getResources(), R.drawable.annie_face_right);
        robotFacingSouth = BitmapFactory.decodeResource(getResources(), R.drawable.annie_face_down);
        robotFacingWest = BitmapFactory.decodeResource(getResources(), R.drawable.annie_face_left);
    }

    @Override
    protected void onSizeChanged(int w, int h, int oldw, int oldh) {
        super.onSizeChanged(w, h, oldw, oldh);

        int gridSize = Grid.GRID_SIZE; // Get grid size from your Grid class

        // Compute cell size dynamically based on parent view size
        cellSize = Math.min(w, h) / (gridSize + 2);

        // Calculate offsets to align RobotView with CanvasView
        offsetX = (w - (gridSize * cellSize)) / 2;
        offsetY = (h - (gridSize * cellSize)) / 2;
    }

    @Override
    protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);

        // Calculate new dimensions to fit the 20cm x 21cm robot in the grid
        int robotWidth = cellSize * 2;  // Robot spans 2 grid cells in width
        int robotHeight = (int) (cellSize * 2.1);  // Robot spans ~2.1 grid cells in height

        // Calculate the position of the robot centered on its current grid cell
        int centerX = offsetX + (robot.getPosition().getXInt() * cellSize) + (cellSize / 2);
        int centerY = offsetY + (Grid.GRID_SIZE - 1 - robot.getPosition().getYInt()) * cellSize + (cellSize / 2);

        // Adjust the position so the robot is centered correctly
        int left = centerX - (robotWidth / 2);
        int top = centerY - (robotHeight / 2);
        int right = left + robotWidth;
        int bottom = top + robotHeight;

        // Choose the correct robot facing bitmap
        Bitmap currentRobotBitmap = switch (robot.getFacing()) {
            case NORTH -> robotFacingNorth;
            case EAST -> robotFacingEast;
            case SOUTH -> robotFacingSouth;
            case WEST -> robotFacingWest;
            case SKIP -> null;
        };

        // Draw the scaled and centered robot bitmap
        if (currentRobotBitmap != null) {
            canvas.drawBitmap(currentRobotBitmap, null, new Rect(left, top, right, bottom), null);
        }
    }

    public void setRobot(Robot robot) {
        this.robot = robot;
        invalidate(); // Refresh the view
    }
}
