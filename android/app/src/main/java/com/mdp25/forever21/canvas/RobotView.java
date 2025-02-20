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
        robotFacingNorth = BitmapFactory.decodeResource(getResources(), R.drawable.car_face_up);
        robotFacingEast = BitmapFactory.decodeResource(getResources(), R.drawable.car_face_right);
        robotFacingSouth = BitmapFactory.decodeResource(getResources(), R.drawable.car_face_down);
        robotFacingWest = BitmapFactory.decodeResource(getResources(), R.drawable.car_face_left);
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

        // Match how obstacles are placed
        int left = offsetX + robot.getPosition().getXInt() * cellSize;
        int top = offsetY + (Grid.GRID_SIZE - 1 - robot.getPosition().getYInt()) * cellSize;
        int right = left + cellSize;
        int bottom = top + cellSize;

        if (robot.getFacing() == Facing.NORTH) {
            canvas.drawBitmap(robotFacingNorth, null, new Rect(left, top, right, bottom), null);
        }
        else if (robot.getFacing() == Facing.EAST) {
            canvas.drawBitmap(robotFacingEast, null, new Rect(left, top, right, bottom), null);
        }
        else if (robot.getFacing() == Facing.SOUTH) {
            canvas.drawBitmap(robotFacingSouth, null, new Rect(left, top, right, bottom), null);
        }
        else if (robot.getFacing() == Facing.WEST) {
            canvas.drawBitmap(robotFacingWest, null, new Rect(left, top, right, bottom), null);
        }
    }

    public void setRobot(Robot robot) {
        this.robot = robot;
        invalidate(); // Refresh the view
    }
}
