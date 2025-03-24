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
    private static int idGen = 1;
    private final List<GridObstacle> obstacleList; // list represents obstacles currently added

    public Grid() {
        obstacleList = new ArrayList<>();
    }

    /**
     * Adds an obstacle to a specified position.
     * <p> Always sets the id of the created obstacle in a incrementing fashion.
     *
     * @param obstacle The GridObstacle object.
     * @return true if placed successfully, false if out of bounds or position occupied.
     */
    public boolean addObstacle(GridObstacle obstacle) {
        // skip check if obstacle not alr at same position
        obstacleList.add(obstacle);
        obstacle.setId(idGen++); // set the id to an auto-inc id
        Log.d(TAG, "Added obstacle: " + obstacle);
        return true;
    }

    /**
     * Removes an obstacle from the specified position.
     *
     * @return true if an obstacle was removed, false if the position was empty.
     */
    public boolean removeObstacle(int x, int y) {
        Optional<GridObstacle> foundObstacle = findObstacleWithPos(x, y);
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
    public Optional<GridObstacle> findObstacleWithPos(int x, int y) {
        for (GridObstacle gridObstacle : obstacleList) {
            if (gridObstacle.getPosition().getXInt() == x &&
                    gridObstacle.getPosition().getYInt() == y) {
                return Optional.of(gridObstacle);
            }
        }
        return Optional.empty();
    }

    /**
     * Gets the obstacle at a given approximate position.
     */
    public Optional<GridObstacle> findObstacleWithApproxPos(int touchX, int touchY, int SELECTION_RADIUS) {
        Optional<GridObstacle> nearestObstacle = Optional.empty();
        double minDistance = SELECTION_RADIUS; // Set threshold distance

        for (GridObstacle obstacle : getObstacleList()) {
            int obsX = obstacle.getPosition().getXInt();
            int obsY = obstacle.getPosition().getYInt();
            double distance = Math.sqrt(Math.pow(touchX - obsX, 2) + Math.pow(touchY - obsY, 2));

            if (distance < minDistance) {
                minDistance = distance;
                nearestObstacle = Optional.of(obstacle);
            }
        }
        return nearestObstacle;
    }

    /**
     * Gets the obstacle from a given id.
     */
    public Optional<GridObstacle> findObstacleWithId(int obstacleId) {
        for (GridObstacle gridObstacle : obstacleList) {
            if (gridObstacle.getId() == obstacleId) {
                return Optional.of(gridObstacle);
            }
        }
        return Optional.empty();
    }

    /**
     * If there is an obstacle at (x,y), returns true
     */
    public boolean hasObstacle(int x, int y) {
        return findObstacleWithPos(x, y).isPresent();
    }

    /**
     * Returns list of obstacles (mutable). For usage in {@link CanvasView}.
     */
    public List<GridObstacle> getObstacleList() {
        return obstacleList;
    }

    public void updateObstacleTarget(int x, int y, int targetId) {
        findObstacleWithPos(x, y).ifPresent(obstacle -> obstacle.setTarget(Target.of(targetId)));
    }

    public void updateObstacleTarget(int obstacleId, int targetId) {
        findObstacleWithId(obstacleId).ifPresent(obstacle -> obstacle.setTarget(Target.of(targetId)));
    }

    public boolean isInsideGrid(int x, int y) {
        return x >= 0 && x < GRID_SIZE && y >= 0 && y < GRID_SIZE;
    }

    /**
     * Clear all obstacles
     */
    public void clear() {
        obstacleList.clear();
    }
}
