package com.mdp25.forever21;

/**
 * Simple static class that provides mapping for target ids to targets.
 */
public class Target {
    // use an array of size 41
    private static String[] map = new String[]{
            "", "", "", "", "", "", "", "", "", "", //0-9th idx
            "bs", // "Bullseye", //10
            "1", // "One",
            "2", // "Two",
            "3", // "Three",
            "4", // "Four",
            "5", // "Five",
            "6", // "Six",
            "7", // "Seven",
            "8", // "Eight",
            "9", // "Nine",
            "A",
            "B",
            "C",
            "D",
            "E",
            "F",
            "G",
            "H",
            "S",
            "T",
            "U",
            "V",
            "W",
            "X",
            "Y",
            "Z",
            "up", // "Up Arrow",
            "dwn", // "Down Arrow",
            "rgt", // "Right Arrow",
            "lft", // "Left Arrow",
            "stp", // "Stop" //40
    };

    public static String get(int targetId) {
        if (targetId >= 10 && targetId <= 40) {
            return map[targetId];
        }
        return "";
    }
}
