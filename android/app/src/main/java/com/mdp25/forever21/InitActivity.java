package com.mdp25.forever21;

import androidx.appcompat.app.AppCompatActivity;

import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;

import com.mdp25.forever21.bluetooth.BluetoothMessageReceiver;

/**
 * Initial launched activity. Only entered once. Doesn't do anything at the moment.
 */
public class InitActivity extends AppCompatActivity {
    private final String TAG = "InitActivity";
    private static boolean entered = false;
    private final long DELAY_TIME_MS = 2000;
    private final Class<?> NEXT_ACTIVITY = BluetoothActivity.class;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        if (entered) {
            Log.e(TAG, "Entered activity twice, is this intentional?");
            return;
        }
        entered = true;
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_init);

        // wait for a tiny amount of time then change to activity
        Log.d(TAG, String.format("Loading starting activity %s in %d", NEXT_ACTIVITY.getName(), DELAY_TIME_MS));
        Handler handler = new Handler(Looper.getMainLooper());
        handler.postDelayed(() -> {
            startActivity(new Intent(this, NEXT_ACTIVITY));
            finish(); // to remove from stack
        }, DELAY_TIME_MS);
    }
}