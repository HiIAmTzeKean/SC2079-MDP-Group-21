package com.mdp25.forever21.canvas;

import com.mdp25.forever21.Facing;
import com.mdp25.forever21.Position;

/**
 * Represents a obstacle that can be placed on the grid.
 * <p> Initially, there is only a facing and ID.
 * <p> Once the robot recognises the number, the relevant (nearest?) obstacle's number is updated.
 */
public class GridObstacle {
    private final Facing facing;
    private final int id; // i.e. which nth obstacle is this?

    // some data too store position?
    private Position position;

    public GridObstacle(Facing facing, int id) {
        this.facing = facing;
        this.id = id;
    }
}
