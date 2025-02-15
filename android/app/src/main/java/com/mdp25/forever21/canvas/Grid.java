package com.mdp25.forever21.canvas;

import java.util.Optional;

/**
 * Logical representation / Data structure for the canvas grid.
 * <p> Most cells are empty, and some contain {@link GridObstacle}s.
 */
public class Grid {
    private static final int GRID_SIZE = 20;
    private final GridObstacle[] grid; // grid is a 1D array because each GridObstacle has a position attribute

    public Grid() { grid = new GridObstacle[GRID_SIZE * GRID_SIZE]; }

    /**
     * Adds an obstacle to a specified position.
     * @param obstacle The GridObstacle object.
     * @param x The x-coordinate (0 to 19).
     * @param y The y-coordinate (0 to 19).
     * @return true if placed successfully, false if out of bounds or position occupied.
     */
    public boolean addObstacle(GridObstacle obstacle, int x, int y) {
        if (isOutOfBounds(x, y) || grid[toIndex(x, y)] != null) {
            return false; // Invalid position or already occupied
        }
        grid[toIndex(x, y)] = obstacle; // Place the obstacle
        return true;
    }

    /**
     * Removes an obstacle from the specified position.
     * @return true if an obstacle was removed, false if the position was empty.
     */
    public boolean removeObstacle(int x, int y) {
        if (isOutOfBounds(x, y)) return false; // Invalid position

        int index = toIndex(x, y);
        if (grid[index] == null) return false; // No obstacle to remove

        grid[index] = null; // Remove the obstacle
        return true;
    }

    /**
     * Gets the obstacle at a given position.
     * @param x The x-coordinate.
     * @param y The y-coordinate.
     * @return The GridObstacle at (x, y), or null if empty.
     */
    public Optional<GridObstacle> getObstacle(int x, int y) {
        if (isOutOfBounds(x, y)) {
            return Optional.empty(); // Out of bounds, return empty
        }
        return Optional.ofNullable(grid[toIndex(x, y)]); // Wrap existing value or null in Optional
    }

    /**
     * Gets the size of the grid.
     */
    public static int getGridSize() {
        return GRID_SIZE;
    }

    /**
     * Helper function that checks if a position is out of the grid bounds.
     */
    private boolean isOutOfBounds(int x, int y) {
        return x < 0 || x >= GRID_SIZE || y < 0 || y >= GRID_SIZE;
    }

    /**
     * Helper function to convert 2D coordinates to 1D index.
     */
    private int toIndex(int x, int y) {
        return x + (y * GRID_SIZE);
    }
}
