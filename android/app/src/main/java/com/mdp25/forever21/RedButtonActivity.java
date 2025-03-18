package com.mdp25.forever21;

import android.content.BroadcastReceiver;
import android.content.IntentFilter;
import android.media.MediaPlayer;
import android.os.Bundle;
import android.view.View;
import android.widget.ImageButton;
import android.widget.ImageView;
import android.widget.Switch;

import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.SwitchCompat;

import com.google.android.material.switchmaterial.SwitchMaterial;
import com.mdp25.forever21.bluetooth.BluetoothMessage;
import com.mdp25.forever21.bluetooth.BluetoothMessageParser;
import com.mdp25.forever21.bluetooth.BluetoothMessageReceiver;

/**
 * Provides a big red button for task 2.
 * Equivalent to pressing "start" on {@link CanvasActivity}.
 */
public class RedButtonActivity extends AppCompatActivity {
    private MyApplication myApp;
    private BroadcastReceiver msgReceiver;
    private MediaPlayer mediaPlayer;
    private ImageButton bigRedBtn;
    private ImageView buttonCover;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_red_button);

        myApp = (MyApplication) getApplication();

        msgReceiver = new BluetoothMessageReceiver(BluetoothMessageParser.ofDefault(), this::onMsgReceived);
        getApplicationContext().registerReceiver(msgReceiver, new IntentFilter(BluetoothMessageReceiver.ACTION_MSG_READ), RECEIVER_NOT_EXPORTED);

        bigRedBtn = (ImageButton) findViewById(R.id.bigRedBtn);
        bigRedBtn.setEnabled(false); // need 2FA for pressing :)
        bigRedBtn.setOnClickListener(view -> {
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

        buttonCover = (ImageView) findViewById(R.id.buttonCover);

        SwitchMaterial buttonSwitch = (SwitchMaterial) findViewById(R.id.switch2fa);
        buttonSwitch.setOnCheckedChangeListener((b, checked) -> {
            bigRedBtn.setEnabled(checked);
            buttonCover.setVisibility(checked ? View.GONE : View.VISIBLE);
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
