package com.mdp25.forever21.canvas;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.util.AttributeSet;
import android.view.View;

import androidx.annotation.NonNull;

import com.mdp25.forever21.Facing;

public class CanvasView extends View {
    private final String TAG = "CanvasView";
    private int cellSize;  // Calculated dynamically
    private int offsetX, offsetY; // To center the grid
    private final Paint gridPaint = new Paint();
    private final Paint textPaint = new Paint();
    private final Paint obstaclePaint = new Paint();
    private final Paint idPaint = new Paint();
    private final Paint facingPaint = new Paint();
    private final Paint targetPaint = new Paint();
    private Grid grid;

    public CanvasView(Context context, AttributeSet attrs) {
        super(context, attrs);
        init();
    }

    @Override
    public boolean performClick() {
        return super.performClick();
    }

    private void init() {
        // Grid styling
        gridPaint.setColor(Color.BLACK);
        gridPaint.setStrokeWidth(2);
        gridPaint.setStyle(Paint.Style.STROKE);

        // Label text styling
        textPaint.setColor(Color.BLACK);
        textPaint.setTextSize(20);  // Adjust for readability
        textPaint.setTextAlign(Paint.Align.CENTER);
        textPaint.setFakeBoldText(true);

        // Obstacle styling
        obstaclePaint.setColor(Color.BLACK);
        obstaclePaint.setStyle(Paint.Style.FILL);

        // ID text styling (obstacle IDs)
        idPaint.setColor(Color.WHITE);
        idPaint.setTextAlign(Paint.Align.CENTER);
        idPaint.setFakeBoldText(false);
        idPaint.setTextSize(25);

        // Target styling
        targetPaint.setColor(Color.GREEN);
        targetPaint.setTextAlign(Paint.Align.CENTER);
        targetPaint.setFakeBoldText(true);
        targetPaint.setTextSize(40);

        // Facing indicator styling (Orange Strip)
        facingPaint.setColor(Color.rgb(255, 165, 0)); // Orange color
        facingPaint.setStyle(Paint.Style.FILL);
    }

    @Override
    protected void onSizeChanged(int w, int h, int oldw, int oldh) {
        super.onSizeChanged(w, h, oldw, oldh);

        int gridSize = Grid.GRID_SIZE;

        // Compute cell size dynamically
        cellSize = Math.min(w, h) / (gridSize + 2); // +2 for axis labels

        // Offset to keep grid centered
        offsetX = (w - (gridSize * cellSize)) / 2;
        offsetY = (h - (gridSize * cellSize)) / 2;
    }

    @Override
    protected void onDraw(@NonNull Canvas canvas) {
        super.onDraw(canvas);
        drawGrid(canvas);
        drawAxisLabels(canvas);
        drawObstacles(canvas);
    }

    private void drawGrid(Canvas canvas) {
        int gridSize = Grid.GRID_SIZE;
        int gridWidth = gridSize * cellSize;
        int gridHeight = gridSize * cellSize;

        for (int i = 0; i <= gridSize; i++) {
            canvas.drawLine(offsetX + i * cellSize, offsetY, offsetX + i * cellSize, offsetY + gridHeight, gridPaint);
            canvas.drawLine(offsetX, offsetY + i * cellSize, offsetX + gridWidth, offsetY + i * cellSize, gridPaint);
        }
    }

    private void drawAxisLabels(Canvas canvas) {
        int gridSize = Grid.GRID_SIZE;
        // Draw X-axis labels (below the grid)
        for (int x = 0; x < gridSize; x++) {
            canvas.drawText(
                    String.valueOf(x),
                    offsetX + x * cellSize + (cellSize / 2),  // Center text
                    offsetY + (gridSize * cellSize) + 30,    // Shift below grid
                    textPaint
            );
        }

        // Draw Y-axis labels (left of the grid)
        for (int y = 0; y < gridSize; y++) {
            canvas.drawText(
                    String.valueOf(y),
                    offsetX - 30,  // Shift left of the grid
                    offsetY + (gridSize - y - 1) * cellSize + (cellSize / 2) + 10,  // Align correctly
                    textPaint
            );
        }
    }

    private void drawObstacles(Canvas canvas) {
        int id = 1;
        for (GridObstacle gridObstacle : grid.getObstacleList()){
            int left = offsetX + gridObstacle.getPosition().getXInt() * cellSize;
            int top = offsetY + (Grid.GRID_SIZE - 1 - gridObstacle.getPosition().getYInt()) * cellSize;  // Flip y-axis
            int right = left + cellSize;
            int bottom = top + cellSize;

            canvas.drawRect(left, top, right, bottom, obstaclePaint);

            // Compute text position (center of cell)
            float textX = left + (cellSize / 2);
            float textY = top + (cellSize / 2) - ((idPaint.descent() + idPaint.ascent()) / 2);

            if(gridObstacle.getTarget() == null){
                // Draw ID text (no target yet)
                canvas.drawText(String.valueOf(gridObstacle.getId()), textX, textY, idPaint);
            }
            else {
                // Draw target text if avail
                canvas.drawText(gridObstacle.getTarget().getTargetStr(), textX, textY, targetPaint);

            }

            // Draw facing indicator
            drawFacingIndicator(canvas, gridObstacle.getFacing(), left, top, right, bottom);
        }
    }

    private void drawFacingIndicator(Canvas canvas, Facing facing, int left, int top, int right, int bottom) {
        int stripThickness = cellSize / 6; // Adjust strip size relative to the cell size

        switch (facing) {
            case NORTH:
                canvas.drawRect(left, top, right, top + stripThickness, facingPaint);
                break;
            case EAST:
                canvas.drawRect(right - stripThickness, top, right, bottom, facingPaint);
                break;
            case SOUTH:
                canvas.drawRect(left, bottom - stripThickness, right, bottom, facingPaint);
                break;
            case WEST:
                canvas.drawRect(left, top, left + stripThickness, bottom, facingPaint);
                break;
        }
    }

    public int getOffsetX() {
        return offsetX;
    }

    public int getOffsetY() {
        return offsetY;
    }

    public int getCellSize() {
        return cellSize;
    }

    public void setGrid(Grid grid) {
        this.grid = grid;
        invalidate(); // Refresh the view
    }
}