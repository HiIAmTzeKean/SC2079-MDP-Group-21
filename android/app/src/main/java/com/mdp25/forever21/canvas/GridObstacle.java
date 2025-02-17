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
    private int id; // id of obstacle
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

    public static GridObstacle of(int x, int y, Facing facing) {
        return new GridObstacle(x, y, facing);
    }

    public void updateFacing(Facing facing){
        this.facing = facing;
    }

    public void updateTarget(Target target){
        this.target = target;
    }

    public void updatePosition(double x, double y) {
        this.position.setX(x);
        this.position.setY(y);
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
