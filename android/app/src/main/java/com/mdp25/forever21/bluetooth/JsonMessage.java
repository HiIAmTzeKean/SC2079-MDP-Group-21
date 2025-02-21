package com.mdp25.forever21.bluetooth;

public interface JsonMessage {
    /**
     * i.e. {"cat": "your-category", "value": "your-value"}
     */
    public static final String FORMAT = "{\"cat\":\"%s\", \"value:\": \"%s\"}";

    /**
     * Same as doing {@code String.format(JsonMessage.FORMAT, category, value)}.
     */
    default String getFormatted(String category, String value) {
        return String.format(JsonMessage.FORMAT, category, value);
    }
    public String getAsJson();
}