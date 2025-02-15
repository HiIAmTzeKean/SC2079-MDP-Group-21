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
    private static int idGen = 1; //incrementing id
    private final int id; // id of obstacle
    private Facing facing;
    private Target target;
    private final Position position;

    public GridObstacle(int x, int y, Facing facing) {
        this.id = idGen++;
        this.facing = facing;
        this.target = null;
        this.position = Position.of(x, y);
    }

    /**
     * Static factory method with default facing of {@link Facing#NORTH}.
     */
    public static GridObstacle of(int x, int y) {
        return new GridObstacle(x, y, Facing.NORTH);
    }

    public int getId() {
        return id;
    }

    public Facing getFacing() {
        return facing;
    }

    public void setFacing(Facing facing){
        this.facing = facing;
    }

    public Target getTarget() {
        return target;
    }

    public void setTarget(Target target){
        this.target = target;
    }

    public Position getPosition() {
        return position;
    }
}
