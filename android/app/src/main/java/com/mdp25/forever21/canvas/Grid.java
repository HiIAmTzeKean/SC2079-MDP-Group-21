package com.mdp25.forever21.canvas;

/**
 * Logical representation / Data structure for the canvas grid.
 * <p> Most cells are empty, and some contain {@link GridObstacle}s.
 */
public class Grid {
    // TODO, add remove obstacles, update obstacle number, update facing, etc.
    private final int rows = 20;
    private final int cols = 20;
    private final GridObstacle[][] grid;

    public Grid() {
        grid = new GridObstacle[rows][cols];
    }

    /**
     * Adds an obstacle to a specified position.
     * @param obstacle The GridObstacle object.
     * @param x The x-coordinate (0 to 19).
     * @param y The y-coordinate (0 to 19).
     * @return true if placed successfully, false if out of bounds or position occupied.
     */
    public boolean addObstacle(GridObstacle obstacle, int x, int y) {
        if (isOutOfBounds(x, y) || grid[x][y] != null) {
            return false; // Invalid position or already occupied
        }
        else {
            grid[x][y] = obstacle; // Place the obstacle
            return true;
        }
    }

    /**
     * Removes an obstacle from the specified position.
     * @param x The x-coordinate (0 to 19).
     * @param y The y-coordinate (0 to 19).
     * @return true if removed successfully, false if position was empty.
     */
    public boolean removeObstacle(int x, int y) {
        if (isOutOfBounds(x, y) || grid[x][y] == null) {
            return false; // Invalid position or no obstacle
        }
        else{
            grid[x][y] = null; // Remove the obstacle
            return true;
        }
    }

    /**
     * Helper function that checks if a position is out of the grid bounds.
     */
    public boolean isOutOfBounds(int x, int y) {
        return x < 0 || x >= rows || y < 0 || y >= cols;
    }

    /**
     * Gets the obstacle at a given position.
     * @param x The x-coordinate.
     * @param y The y-coordinate.
     * @return The GridObstacle at (x, y), or null if empty.
     */
    public GridObstacle getObstacle(int x, int y) {
        if (isOutOfBounds(x, y) || grid[x][y] == null) {
            return null; // Invalid position or no obstacle
        }
        return grid[x][y];
    }

    /**
     * Displays the grid in a simple format for debugging.
     */
    public void printGrid() {
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                System.out.print((grid[i][j] == null ? "." : "X") + " ");
            }
            System.out.println();
        }
    }
}
