package com.mdp25.forever21.bluetooth;

import org.json.JSONObject;

public interface JsonMessage {
    /**
     * i.e. {"cat": "your-category", "value": "your-value"}
     * OR {"cat": "your-category", "value": {}}
     */
    public static final String FORMAT_STR = "{\"cat\":\"%s\", \"value\": \"%s\"}";
    public static final String FORMAT_OBJ = "{\"cat\":\"%s\", \"value\": %s}";

    /**
     * Same as doing {@code String.format(JsonMessage.FORMAT, category, value)}.
     */
    default String getFormattedStr(String category, String value) {
        return String.format(JsonMessage.FORMAT_STR, category, value);
    }
    default String getFormattedObj(String category, JSONObject obj) {
        return String.format(JsonMessage.FORMAT_OBJ, category, obj);
    }
    public String getAsJson();
}