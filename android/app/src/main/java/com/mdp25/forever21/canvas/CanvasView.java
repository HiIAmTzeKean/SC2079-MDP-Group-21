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
    private final Paint obstacleSelectedPaint = new Paint();
    private final Paint obstaclePaint = new Paint();
    private final Paint idPaint = new Paint();
    private final Paint facingPaint = new Paint();
    private final Paint targetPaint = new Paint();
    private final Paint startRegionPaint = new Paint();
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
        // grid styling
        gridPaint.setColor(Color.BLACK);
        gridPaint.setStrokeWidth(2);
        gridPaint.setStyle(Paint.Style.STROKE);

        // label text styling
        textPaint.setColor(Color.BLACK);
        textPaint.setTextSize(20);  // Adjust for readability
        textPaint.setTextAlign(Paint.Align.CENTER);
        textPaint.setFakeBoldText(true);

        // obstacle styling
        obstaclePaint.setColor(Color.BLACK);
        obstaclePaint.setStyle(Paint.Style.FILL);
        obstacleSelectedPaint.setColor(Color.GRAY);
        obstacleSelectedPaint.setStyle(Paint.Style.FILL);

        // ID text styling (obstacle IDs)
        idPaint.setColor(Color.WHITE);
        idPaint.setTextAlign(Paint.Align.CENTER);
        idPaint.setFakeBoldText(false);
        idPaint.setTextSize(16);

        // target styling
        targetPaint.setColor(Color.GREEN);
        targetPaint.setTextAlign(Paint.Align.CENTER);
        targetPaint.setFakeBoldText(true);
        targetPaint.setTextSize(24);

        // facing indicator styling (Orange)
        facingPaint.setColor(Color.rgb(255, 165, 0));
        facingPaint.setStyle(Paint.Style.FILL);

        // initialize startRegionPaint
        startRegionPaint.setColor(Color.GREEN);
        startRegionPaint.setStrokeWidth(4);
        startRegionPaint.setStyle(Paint.Style.STROKE);
    }

    @Override
    protected void onSizeChanged(int w, int h, int oldw, int oldh) {
        super.onSizeChanged(w, h, oldw, oldh);

        int gridSize = Grid.GRID_SIZE;

        // cell size dynamic computation
        cellSize = Math.min(w, h) / (gridSize + 2); // +2 for axis labels

        // offset to center grid
        offsetX = (w - (gridSize * cellSize)) / 2;
        offsetY = (h - (gridSize * cellSize)) / 2;
    }

    @Override
    protected void onDraw(@NonNull Canvas canvas) {
        super.onDraw(canvas);
        drawGrid(canvas);
        drawStartRegion(canvas);
        drawAxisLabels(canvas);
        drawObstacles(canvas);
    }

    private void drawGrid(Canvas canvas) {
        int gridSize = Grid.GRID_SIZE;
        int gridWidth = gridSize * cellSize;
        int gridHeight = gridSize * cellSize;

        Paint redPaint = new Paint();
        redPaint.setColor(Color.RED);
        redPaint.setStrokeWidth(2);
        redPaint.setStyle(Paint.Style.STROKE);

        Paint bluePaint = new Paint();
        bluePaint.setColor(Color.BLUE);
        bluePaint.setStrokeWidth(2);
        bluePaint.setStyle(Paint.Style.STROKE);

        // draw vertical grid lines with alternating colors
        for (int i = 0; i <= gridSize; i++) {
            Paint paintToUse = (i % 2 == 0) ? redPaint : bluePaint;
            canvas.drawLine(offsetX + i * cellSize, offsetY, offsetX + i * cellSize, offsetY + gridHeight, paintToUse);
        }

        // draw horizontal grid lines with alternating colors
        for (int i = 0; i <= gridSize; i++) {
            Paint paintToUse = (i % 2 == 0) ? bluePaint : redPaint;
            canvas.drawLine(offsetX, offsetY + i * cellSize, offsetX + gridWidth, offsetY + i * cellSize, paintToUse);
        }
    }

    private void drawStartRegion(Canvas canvas) {
        int left = offsetX;
        int right = offsetX + (4 * cellSize);
        int top = offsetY + ((Grid.GRID_SIZE - 4) * cellSize); // flip y-axis
        int bottom = offsetY + (Grid.GRID_SIZE * cellSize);

        // draw the green boundary lines
        canvas.drawLine(left, bottom, right, bottom, startRegionPaint); // bottom line (0,0) to (4,0)
        canvas.drawLine(left, top, right, top, startRegionPaint);       // top line (0,4) to (4,4)
        canvas.drawLine(left, top, left, bottom, startRegionPaint);     // left line (0,0) to (0,4)
        canvas.drawLine(right, top, right, bottom, startRegionPaint);   // right line (4,0) to (4,4)
    }

    private void drawAxisLabels(Canvas canvas) {
        int gridSize = Grid.GRID_SIZE;

        // adjustments for positioning
        float yLabelOffsetY = cellSize / 4f;  // shift down for Y-axis labels

        // draw X-axis labels
        for (int x = 0; x < gridSize; x++) {
            if (x == 0) continue; // skip drawing "0" here to avoid duplication at (0,0)
            canvas.drawText(
                    String.valueOf(x),
                    offsetX + x * cellSize,  // align with left vertical grid line
                    offsetY + (gridSize * cellSize) + 30,    // shift below grid
                    textPaint
            );
        }

        // draw Y-axis labels
        for (int y = 0; y < gridSize; y++) {
            if (y == 0) continue; // skip drawing "0" here to avoid duplication at (0,0)
            canvas.drawText(
                    String.valueOf(y),
                    offsetX - 30,  // shift left of the grid
                    offsetY + (gridSize - y) * cellSize + yLabelOffsetY,  // align with bottom horizontal grid line
                    textPaint
            );
        }

        // draw (0,0)
        canvas.drawText(
                "0",
                offsetX - 30,  // align to left of the grid
                offsetY + (gridSize * cellSize) + 30,  // align to bottom of the grid
                textPaint
        );
    }

    private void drawObstacles(Canvas canvas) {
        int id = 1;
        for (GridObstacle gridObstacle : grid.getObstacleList()){
            int left = offsetX + gridObstacle.getPosition().getXInt() * cellSize;
            int top = offsetY + (Grid.GRID_SIZE - 1 - gridObstacle.getPosition().getYInt()) * cellSize;  // Flip y-axis
            int right = left + cellSize;
            int bottom = top + cellSize;

            boolean selected = gridObstacle.isSelected();
            canvas.drawRect(left, top, right, bottom, selected ? obstacleSelectedPaint : obstaclePaint);

            // compute center of cell for text position
            float textX = left + (cellSize / 2);
            float textY = top + (cellSize / 2) - ((idPaint.descent() + idPaint.ascent()) / 2);

            if(gridObstacle.getTarget() == null){
                // draw ID text where there is no target
                canvas.drawText(String.valueOf(gridObstacle.getId()), textX, textY, idPaint);
            }
            else {
                // draw target text where there is a target
                canvas.drawText(gridObstacle.getTarget().getTargetStr(), textX, textY, targetPaint);
            }

            // draw facing indicator
            drawFacingIndicator(canvas, gridObstacle.getFacing(), left, top, right, bottom);
        }
    }

    private void drawFacingIndicator(Canvas canvas, Facing facing, int left, int top, int right, int bottom) {
        int stripThickness = cellSize / 6; // adjust strip size relative to the cell size

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
        invalidate();
    }
}