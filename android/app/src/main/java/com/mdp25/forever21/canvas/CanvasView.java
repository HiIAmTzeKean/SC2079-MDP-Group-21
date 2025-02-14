package com.mdp25.forever21.canvas;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.util.AttributeSet;
import android.view.View;

import java.util.HashMap;
import java.util.Map;

public class CanvasView extends View {
    private static final int GRID_SIZE = 20;  // 20x20 grid
    private int cellSize;  // Calculated dynamically
    private int offsetX, offsetY; // To center the grid

    private final Paint gridPaint = new Paint();
    private final Paint textPaint = new Paint();
    private final Paint obstaclePaint = new Paint();

    private final Map<String, GridObstacle> obstacles = new HashMap<>();

    public CanvasView(Context context, AttributeSet attrs) {
        super(context, attrs);
        init();
        setOnTouchListener(new CanvasTouchController(this));
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
        obstaclePaint.setColor(Color.rgb(255, 165, 0));
        obstaclePaint.setStyle(Paint.Style.FILL);
    }

    @Override
    protected void onSizeChanged(int w, int h, int oldw, int oldh) {
        super.onSizeChanged(w, h, oldw, oldh);

        // Compute cell size dynamically
        cellSize = Math.min(w, h) / (GRID_SIZE + 2); // +2 for axis labels

        // Offset to keep grid centered
        offsetX = (w - (GRID_SIZE * cellSize)) / 2;
        offsetY = (h - (GRID_SIZE * cellSize)) / 2;

        invalidate(); // Redraw with new dimensions
    }

    @Override
    protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);
        drawGrid(canvas);
        drawAxisLabels(canvas);
        drawObstacles(canvas);
    }

    private void drawGrid(Canvas canvas) {
        int gridWidth = GRID_SIZE * cellSize;
        int gridHeight = GRID_SIZE * cellSize;

        // Draw vertical and horizontal grid lines
        for (int i = 0; i <= GRID_SIZE; i++) {
            // Vertical lines
            canvas.drawLine(offsetX + i * cellSize, offsetY, offsetX + i * cellSize, offsetY + gridHeight, gridPaint);
            // Horizontal lines
            canvas.drawLine(offsetX, offsetY + i * cellSize, offsetX + gridWidth, offsetY + i * cellSize, gridPaint);
        }
    }

    private void drawAxisLabels(Canvas canvas) {
        // Draw X-axis labels (below the grid)
        for (int x = 0; x < GRID_SIZE; x++) {
            canvas.drawText(
                    String.valueOf(x),
                    offsetX + x * cellSize + (cellSize / 2),  // Center text
                    offsetY + (GRID_SIZE * cellSize) + 30,    // Shift below grid
                    textPaint
            );
        }

        // Draw Y-axis labels (left of the grid)
        for (int y = 0; y < GRID_SIZE; y++) {
            canvas.drawText(
                    String.valueOf(y),
                    offsetX - 30,  // Shift left of the grid
                    offsetY + (GRID_SIZE - y - 1) * cellSize + (cellSize / 2) + 10,  // Align correctly
                    textPaint
            );
        }
    }

    private void drawObstacles(Canvas canvas) {
        for (Map.Entry<String, GridObstacle> entry : obstacles.entrySet()) {
            GridObstacle obstacle = entry.getValue();
            int x = obstacle.getPosition().getXInt();
            int y = obstacle.getPosition().getYInt();

            int left = offsetX + x * cellSize;
            int top = offsetY + (GRID_SIZE - 1 - y) * cellSize;  // Flip y-axis
            int right = left + cellSize;
            int bottom = top + cellSize;

            canvas.drawRect(left, top, right, bottom, obstaclePaint);
        }
    }

    public void addObstacle(int x, int y) {
        if (x >= 0 && x < GRID_SIZE && y >= 0 && y < GRID_SIZE) {
            String key = x + "," + y;
            obstacles.put(key, GridObstacle.of(x, y));
            invalidate();  // Redraw canvas
        }
    }

    public void removeObstacle(int x, int y) {
        String key = x + "," + y;
        obstacles.remove(key);
        invalidate();  // Redraw canvas
    }

    public int getGridSize() {
        return GRID_SIZE;
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

    public boolean hasObstacle(int x, int y) {
        return obstacles.containsKey(x + "," + y);
    }

    public GridObstacle getObstacle(int x, int y) {
        return obstacles.get(x + "," + y);
    }
}