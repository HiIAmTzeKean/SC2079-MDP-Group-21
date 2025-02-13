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
    private int id; // id of obstacle
    private Facing facing;
    private Target target;
    private Position position;

    public GridObstacle(int x, int y) {
        this.facing = Facing.NORTH;
        this.id = 0;
        this.target = null;
        this.position = new Position();
        this.position.setX(x);
        this.position.setY(y);
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

    public void setId(int id) {
        this.id = id;
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
