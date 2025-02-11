package com.mdp25.forever21.canvas;

import com.mdp25.forever21.Facing;
import com.mdp25.forever21.Position;
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
    private Position position;

    public GridObstacle(int id) {
        this.facing = Facing.NORTH;
        this.id = id;
        this.target = null;
        this.position = new Position(); //TODO
    }

    public void updateFacing(Facing facing){
        this.facing = facing;
    }

    public void updateTarget(Target target){
        this.target = target;
    }

    public int getId() {
        return id;
    }

    public Facing getFacing() {
        return facing;
    }

    public Target getTarget() {
        return target;
    }

    public Position getPosition() {
        return position;
    }
}
