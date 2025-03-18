package com.mdp25.forever21;

import android.content.BroadcastReceiver;
import android.content.IntentFilter;
import android.media.MediaPlayer;
import android.os.Bundle;

import androidx.appcompat.app.AppCompatActivity;

import com.mdp25.forever21.bluetooth.BluetoothMessage;
import com.mdp25.forever21.bluetooth.BluetoothMessageParser;
import com.mdp25.forever21.bluetooth.BluetoothMessageReceiver;


public class RedButtonActivity extends AppCompatActivity {
    private MyApplication myApp;
    private BroadcastReceiver msgReceiver;
    private MediaPlayer mediaPlayer;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_red_button);

        myApp = (MyApplication) getApplication();

        msgReceiver = new BluetoothMessageReceiver(BluetoothMessageParser.ofDefault(), this::onMsgReceived);
        getApplicationContext().registerReceiver(msgReceiver, new IntentFilter(BluetoothMessageReceiver.ACTION_MSG_READ), RECEIVER_NOT_EXPORTED);

        findViewById(R.id.bigRedBtn).setOnClickListener(view -> {
            if (myApp.btConnection() != null){
                BluetoothMessage msg = BluetoothMessage.ofRobotStartMessage();
                myApp.btConnection().sendMessage(msg.getAsJsonMessage().getAsJson());
                if (mediaPlayer != null) {
                    mediaPlayer.stop();
                    mediaPlayer.release();
                }
                mediaPlayer = MediaPlayer.create(this, R.raw.thomas_bass_boosted);
                mediaPlayer.start();
            }
        });
    }

    private void onMsgReceived(BluetoothMessage btMsg) {
        if (btMsg instanceof BluetoothMessage.RobotStatusMessage m) {
            if (m.status().equals("finished")) {
                if (mediaPlayer != null) {
                    mediaPlayer.stop();
                    mediaPlayer.release();
                }
                mediaPlayer = MediaPlayer.create(this, R.raw.yippee);
                mediaPlayer.start();
            }
        }
    }
}
