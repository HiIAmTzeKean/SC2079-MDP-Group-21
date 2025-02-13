package com.mdp25.forever21.canvas;

import android.view.MotionEvent;
import android.view.View;
import android.animation.ValueAnimator;

/**
 * Handles all touch interactions with the canvas. Namely:
 * <ul>
 *     <li>Touch empty grid space to add obstacle</li>
 *     <li>Touch & hold in an occupied spot, then drag to move/remove obstacle</li>
 * </ul>
 * Extra: Uses vibration to feedback to the user.
 */
public class CanvasTouchController implements View.OnTouchListener {
    private final CanvasView canvasView;
    private GridObstacle selectedObstacle = null;
    private int selectedX = -1, selectedY = -1;
    private float animatedX, animatedY; // For smooth movement

    public CanvasTouchController(CanvasView canvasView) {
        this.canvasView = canvasView;
    }

    @Override
    public boolean onTouch(View v, MotionEvent event) {
        int x = (int) ((event.getX() - canvasView.getOffsetX()) / canvasView.getCellSize());
        int y = (int) ((event.getY() - canvasView.getOffsetY()) / canvasView.getCellSize());

        // Flip Y to match bottom-left origin
        y = (canvasView.getGridSize() - 1) - y;

        switch (event.getAction()) {
            case MotionEvent.ACTION_DOWN:
                // Start drag if obstacle exists
                if (canvasView.hasObstacle(x, y)) {
                    selectedObstacle = canvasView.getObstacle(x, y);
                    selectedX = x;
                    selectedY = y;
                    animatedX = x * canvasView.getCellSize();
                    animatedY = y * canvasView.getCellSize();
                }
                else {
                    canvasView.addObstacle(x, y);
                }
                break;

            case MotionEvent.ACTION_MOVE:
                if (selectedObstacle != null) {
                    // Remove from old position
                    canvasView.removeObstacle(selectedX, selectedY);
                    selectedX = x;
                    selectedY = y;
                }
                break;

            case MotionEvent.ACTION_UP:
                if (selectedObstacle != null) {
                    if (x >= 0 && x < canvasView.getGridSize() && y >= 0 && y < canvasView.getGridSize()) {
                        // Place in new position
                        canvasView.addObstacle(x, y);
                    } else {
                        // Remove obstacle if dragged out of bounds
                        canvasView.removeObstacle(selectedX, selectedY);
                    }
                    selectedObstacle = null;
                }
                break;
        }
        canvasView.invalidate(); // Refresh canvas
        return true;
    }
}
