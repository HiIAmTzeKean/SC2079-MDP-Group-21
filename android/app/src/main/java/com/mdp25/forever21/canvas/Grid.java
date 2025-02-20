package com.mdp25.forever21.canvas;

import android.util.Log;

import com.mdp25.forever21.Target;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

/**
 * Logical representation / Data structure for the canvas grid.
 * <p> Contains {@link GridObstacle}s.
 */
public class Grid {

    private static final String TAG = "Grid";
    public static final int GRID_SIZE = 20;
    private final List<GridObstacle> obstacleList; // list represents obstacles currently added

    public Grid() {
        obstacleList = new ArrayList<>();
    }

    /**
     * Adds an obstacle to a specified position.
     *
     * @param obstacle The GridObstacle object.
     * @return true if placed successfully, false if out of bounds or position occupied.
     */
    public boolean addObstacle(GridObstacle obstacle) {
        //TODO check if obstacle not alr at same position
        obstacleList.add(obstacle);
        Log.d(TAG, "Added obstacle: " + obstacle);
        return true;
    }

    /**
     * Removes an obstacle from the specified position.
     *
     * @return true if an obstacle was removed, false if the position was empty.
     */
    public boolean removeObstacle(int x, int y) {
        Optional<GridObstacle> foundObstacle = findObstacle(x, y);
        if (foundObstacle.isPresent()) {
            obstacleList.remove(foundObstacle.get());
            Log.d(TAG, "Removed obstacle: " + foundObstacle.get());
            return true;
        }
        return false;
    }

    /**
     * Gets the obstacle at a given position.
     */
    public Optional<GridObstacle> findObstacle(int x, int y) {
        for (GridObstacle gridObstacle : obstacleList) {
            if (gridObstacle.getPosition().getXInt() == x &&
                    gridObstacle.getPosition().getYInt() == y) {
                return Optional.of(gridObstacle);
            }
        }
        return Optional.empty();
    }

    /**
     * If there is an obstacle at (x,y), returns true
     */
    public boolean hasObstacle(int x, int y) {
        return findObstacle(x, y).isPresent();
    }

    /**
     * Returns list of obstacles (mutable). For usage in {@link CanvasView}.
     */
    public List<GridObstacle> getObstacleList() {
        return obstacleList;
    }

    public void updateObstacleTarget(int x, int y, int targetId) {
        findObstacle(x, y).ifPresent(obstacle -> obstacle.setTarget(Target.of(targetId)));
    }

    public boolean isInsideGrid(int x, int y) {
        return x >= 0 && x < GRID_SIZE && y >= 0 && y < GRID_SIZE;
    }
}
