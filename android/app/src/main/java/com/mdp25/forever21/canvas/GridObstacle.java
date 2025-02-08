package com.mdp25.forever21.canvas;

import com.mdp25.forever21.Facing;
import com.mdp25.forever21.Target;

/**
 * Represents a obstacle that can be placed on the grid.
 * <p> Initially, there is only a Facing, ID, and Target.
 * <p> Default facing is set to NORTH and target to null.
 */
public class GridObstacle {
    private final int id; // id of obstacle
    private Facing facing;
    private Target target;

    public GridObstacle(int id) {
        this.facing = Facing.NORTH;
        this.id = id;
        this.target = null;
    }

    public void updateFacing(Facing facing){
        this.facing = facing;
    }

    public void updateTarget(Target target){
        this.target = target;
    }
}
