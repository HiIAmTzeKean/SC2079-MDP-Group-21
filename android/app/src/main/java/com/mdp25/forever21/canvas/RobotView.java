package com.mdp25.forever21.canvas;

import android.content.Context;
import android.graphics.Rect;
import android.util.AttributeSet;
import android.view.View;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Canvas;

import com.mdp25.forever21.R;


public class RobotView extends View {
    private static final String TAG = "RobotView";
    private Bitmap robotFacingNorth;
    private Bitmap robotFacingEast;
    private Bitmap robotFacingSouth;
    private Bitmap robotFacingWest;
    private int cellSize;
    private int offsetX, offsetY;
    private Robot robot;

    public RobotView(Context context, AttributeSet attrs) {
        super(context, attrs);
        init();
    }

    private void init() {
        robotFacingNorth = BitmapFactory.decodeResource(getResources(), R.drawable.annie_face_up);
        robotFacingEast = BitmapFactory.decodeResource(getResources(), R.drawable.annie_face_right);
        robotFacingSouth = BitmapFactory.decodeResource(getResources(), R.drawable.annie_face_down);
        robotFacingWest = BitmapFactory.decodeResource(getResources(), R.drawable.annie_face_left);
    }

    @Override
    protected void onSizeChanged(int w, int h, int oldw, int oldh) {
        super.onSizeChanged(w, h, oldw, oldh);

        int gridSize = Grid.GRID_SIZE;

        // cell size dynamic computation
        cellSize = Math.min(w, h) / (gridSize + 2);

        // offsets to align RobotView with CanvasView
        offsetX = (w - (gridSize * cellSize)) / 2;
        offsetY = (h - (gridSize * cellSize)) / 2;
    }

    @Override
    protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);

        int robotWidth = cellSize * 2;
        int robotHeight = (int) (cellSize * 2.1);

        // calculate the position of the robot centered on its current grid cell
        int centerX = offsetX + (robot.getPosition().getXInt() * cellSize) + (cellSize / 2);
        int centerY = offsetY + (Grid.GRID_SIZE - 1 - robot.getPosition().getYInt()) * cellSize + (cellSize / 2);

        // adjust the position so the robot is centered correctly
        int left = centerX - (robotWidth / 2);
        int top = centerY - (robotHeight / 2);
        int right = left + robotWidth;
        int bottom = top + robotHeight;

        Bitmap currentRobotBitmap = switch (robot.getFacing()) {
            case NORTH -> robotFacingNorth;
            case EAST -> robotFacingEast;
            case SOUTH -> robotFacingSouth;
            case WEST -> robotFacingWest;
            case SKIP -> null;
        };

        // draw the scaled and centered robot bitmap
        if (currentRobotBitmap != null) {
            canvas.drawBitmap(currentRobotBitmap, null, new Rect(left, top, right, bottom), null);
        }
    }

    public void setRobot(Robot robot) {
        this.robot = robot;
        invalidate();
    }
}
