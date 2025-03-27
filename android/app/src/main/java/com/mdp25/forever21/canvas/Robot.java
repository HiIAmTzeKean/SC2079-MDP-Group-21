package com.mdp25.forever21.canvas;

import com.mdp25.forever21.Facing;
import com.mdp25.forever21.Position;

public class Robot {
    private Facing facing;
    private final Position position;
    private final double turningRadius = 4.5;

    public Robot(int x, int y, Facing facing) {
        this.facing = facing;
        this.position = Position.of(x, y);
    }

    public static Robot ofDefault() {
        return new Robot(1, 1, Facing.NORTH);
    }

    /**
     * Static factory method with default facing of {@link Facing#NORTH}.
     */
    public static Robot of(int x, int y) {
        return new Robot(x, y, Facing.NORTH);
    }

    public static Robot of(int x, int y, Facing facing) {
        return new Robot(x, y, facing);
    }

    public Robot updatePosition(int x, int y) {
        position.setX(x);
        position.setY(y);
        return this;
    }

    public Position getPosition() {
        return this.position;
    }

    public Robot updateFacing(Facing facing) {
        if (!facing.equals(Facing.SKIP))
            this.facing = facing;
        return this;
    }

    public Facing getFacing() {
        return this.facing;
    }
}
