package com.mdp25.forever21.canvas;

import com.mdp25.forever21.Facing;
import com.mdp25.forever21.Position;
import com.mdp25.forever21.Target;

import java.util.Objects;

/**
 * Represents a obstacle that can be placed on the grid.
 * <p> Initially, there is only a Facing, ID, and Target.
 * <p> Default facing is set to NORTH and target to null.
 */
public class GridObstacle {
    private int id; // id of obstacle
    private Facing facing;
    private Target target;
    private final Position position;

    private boolean selected; // to detect if the obstacle is being interacted with

    public GridObstacle(int x, int y, Facing facing) {
        this.id = 1;
        this.facing = facing;
        this.target = null;
        this.position = Position.of(x, y);
        this.selected = false;
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

    /**
     * Let parent class manage incrementing id. Care needed.
     */
    public void setId(int id) {
        this.id = id;
    }

    public int getId() {
        return id;
    }

    public Facing getFacing() {
        return facing;
    }

    public void setFacing(Facing facing) {
        this.facing = facing;
    }

    public Target getTarget() {
        return target;
    }

    public void setTarget(Target target) {
        this.target = target;
    }

    public Position getPosition() {
        return position;
    }

    public void updatePosition(int x, int y) {
        position.setX(x);
        position.setY(y);
    }

    public void rotateClockwise() {
        if (this.facing == Facing.NORTH) {
            this.facing = Facing.EAST;
        } else if (this.facing == Facing.EAST) {
            this.facing = Facing.SOUTH;
        } else if (this.facing == Facing.SOUTH) {
            this.facing = Facing.WEST;
        } else if (this.facing == Facing.WEST) {
            this.facing = Facing.NORTH;
        }
    }

    public boolean isSelected() {
        return selected;
    }

    public void setSelected(boolean selected) {
        this.selected = selected;
    }

    @Override
    public String toString() {
        return "GridObstacle{" +
                "id=" + id +
                ", facing=" + facing +
                ", target=" + target +
                ", position=" + position +
                '}';
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        GridObstacle that = (GridObstacle) o;
        return id == that.id;
    }

    @Override
    public int hashCode() {
        return Objects.hash(id, facing, target, position);
    }
}
