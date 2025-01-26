package com.mdp25.forever21;

import androidx.appcompat.app.AppCompatActivity;

import android.os.Bundle;

import com.mdp25.forever21.bluetooth.BluetoothInterface;

public class BluetoothActivity extends AppCompatActivity {

    private BluetoothInterface bluetoothInterface;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_bluetooth);

        bluetoothInterface = new BluetoothInterface();
    }
}