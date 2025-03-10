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

    // Robot moves forward by one cell in the direction it is facing
    public void moveForward() {
        if (this.facing == Facing.NORTH) {
            this.position.setY(this.position.getYInt() + 1);
        } else if (this.facing == Facing.EAST) {
            this.position.setX(this.position.getXInt() + 1);
        } else if (this.facing == Facing.SOUTH) {
            this.position.setY(this.position.getYInt() - 1);
        } else if (this.facing == Facing.WEST) {
            this.position.setX(this.position.getXInt() - 1);
        }
    }

    // Robot moves backward by one cell in the direction it is facing
    public void moveBackward() {
        if (this.facing == Facing.NORTH) {
            this.position.setY(this.position.getYInt() - 1);
        } else if (this.facing == Facing.EAST) {
            this.position.setX(this.position.getXInt() - 1);
        } else if (this.facing == Facing.SOUTH) {
            this.position.setY(this.position.getYInt() + 1);
        } else if (this.facing == Facing.WEST) {
            this.position.setX(this.position.getXInt() + 1);
        }
    }

    // Robot turns right by moving forward by one cell and the turning radius
    public void turnRight() {
        if (this.facing == Facing.NORTH) {
            this.position.setY(this.position.getYInt() + 1);
            this.position.setX(this.position.getXInt() + turningRadius);
            this.facing = Facing.EAST;
        } else if (this.facing == Facing.EAST) {
            this.position.setX(this.position.getXInt() + 1);
            this.position.setY(this.position.getYInt() - turningRadius);
            this.facing = Facing.SOUTH;
        } else if (this.facing == Facing.SOUTH) {
            this.position.setY(this.position.getYInt() - 1);
            this.position.setX(this.position.getXInt() - turningRadius);
            this.facing = Facing.WEST;
        } else if (this.facing == Facing.WEST) {
            this.position.setX(this.position.getXInt() - 1);
            this.position.setY(this.position.getYInt() + turningRadius);
            this.facing = Facing.NORTH;
        }
    }

    // Robot turns left by moving forward by one cell and the turning radius
    public void turnLeft() {
        if (this.facing == Facing.NORTH) {
            this.position.setY(this.position.getYInt() + 1);
            this.position.setX(this.position.getXInt() - turningRadius);
            this.facing = Facing.WEST;
        } else if (this.facing == Facing.WEST) {
            this.position.setX(this.position.getXInt() - 1);
            this.position.setY(this.position.getYInt() - turningRadius);
            this.facing = Facing.SOUTH;
        } else if (this.facing == Facing.SOUTH) {
            this.position.setY(this.position.getYInt() - 1);
            this.position.setX(this.position.getXInt() + turningRadius);
            this.facing = Facing.EAST;
        } else if (this.facing == Facing.EAST) {
            this.position.setX(this.position.getXInt() + 1);
            this.position.setY(this.position.getYInt() + turningRadius);
            this.facing = Facing.NORTH;
        }
    }

    // Ummm... idk if reverseLeft and reverseRight will ever be implemented. Can delete if not required.
    // Robot reverses left by moving backward by one cell and the turning radius
    public void reverseLeft() {
        if (this.facing == Facing.NORTH) {
            this.position.setY(this.position.getYInt() - 1);
            this.position.setX(this.position.getXInt() - turningRadius);
            this.facing = Facing.EAST;
        } else if (this.facing == Facing.EAST) {
            this.position.setX(this.position.getXInt() - 1);
            this.position.setY(this.position.getYInt() + turningRadius);
            this.facing = Facing.SOUTH;
        } else if (this.facing == Facing.SOUTH) {
            this.position.setY(this.position.getYInt() + 1);
            this.position.setX(this.position.getXInt() + turningRadius);
            this.facing = Facing.WEST;
        } else if (this.facing == Facing.WEST) {
            this.position.setX(this.position.getXInt() + 1);
            this.position.setY(this.position.getYInt() - turningRadius);
            this.facing = Facing.NORTH;
        }
    }

    // Robot reverses right by moving backward by one cell and the turning radius
    public void reverseRight() {
        if (this.facing == Facing.NORTH) {
            this.position.setY(this.position.getYInt() - 1);
            this.position.setX(this.position.getXInt() + turningRadius);
            this.facing = Facing.WEST;
        } else if (this.facing == Facing.WEST) {
            this.position.setX(this.position.getXInt() + 1);
            this.position.setY(this.position.getYInt() + turningRadius);
            this.facing = Facing.SOUTH;
        } else if (this.facing == Facing.SOUTH) {
            this.position.setY(this.position.getYInt() + 1);
            this.position.setX(this.position.getXInt() - turningRadius);
            this.facing = Facing.EAST;
        } else if (this.facing == Facing.EAST) {
            this.position.setX(this.position.getXInt() - 1);
            this.position.setY(this.position.getYInt() - turningRadius);
            this.facing = Facing.NORTH;
        }
    }
}
