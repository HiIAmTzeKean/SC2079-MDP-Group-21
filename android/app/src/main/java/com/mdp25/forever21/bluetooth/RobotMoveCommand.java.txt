package com.mdp25.forever21.bluetooth;

public enum RobotMoveCommand {
    TURN_RIGHT("tr"),
    TURN_LEFT("tl"),
    FORWARD("f"),
    REVERSE("r");

    private final String value;
    RobotMoveCommand(String val) {
        this.value = val;
    }
    public String value() {
        return value;
    }
}
