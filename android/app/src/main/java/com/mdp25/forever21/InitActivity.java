package com.mdp25.forever21;

import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.os.Bundle;
import android.util.Log;

/**
 * Initial launched activity. Holds the main context, such as the static {@link AppContext}.
 */
public class InitActivity extends AppCompatActivity {
    private final String TAG = "InitActivity";
    private static AppContext appContext = null;

    private final Class<?> NEXT_ACITIVTY = BluetoothActivity.class;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_init);
        appContext = new AppContext(); //init static var here

        // TODO pass app context to other activities
        // Change to bluetooth activity
        Log.d(TAG, "Created AppContext, starting activity " + NEXT_ACITIVTY.getName());
        Intent intent = new Intent(this, NEXT_ACITIVTY);
        startActivity(intent);
    }

    public static AppContext getAppContext() {
        if (appContext == null) {
            // not yet created, should not be possible
            throw new RuntimeException("App Context is not yet created. Please only call in Activity.onCreate()");
        }
        return appContext;
    }
}