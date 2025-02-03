package com.mdp25.forever21;

/**
 * Simple enum for heading/direction/facing.
 */
public enum Facing {
    NORTH(0),
    EAST(2),
    SOUTH(4),
    WEST(6),
    SKIP(8);

    private int mappedCode;

    Facing(int code) {
        mappedCode = code;
    }

    /**
     * @return the mapped integer to represent the direction
     */
    public int getMappedCode() {
        return mappedCode;
    }

    public static Facing getFacingFromCode(int code) {
        return switch (code) {
            case 0 -> NORTH;
            case 2 -> EAST;
            case 4 -> SOUTH;
            case 6 -> WEST;
            case 8 -> SKIP;
            default -> NORTH;
        };
    }
}
