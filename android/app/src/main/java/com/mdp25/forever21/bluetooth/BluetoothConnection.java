package com.mdp25.forever21.bluetooth;

import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothSocket;
import android.content.Context;
import android.content.Intent;
import android.util.Log;

import androidx.localbroadcastmanager.content.LocalBroadcastManager;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.charset.Charset;
import java.nio.charset.StandardCharsets;

/**
 * Class responsible for the thread handling incoming/outgoing messages.
 * <p> Reference: <a href="https://developer.android.com/develop/connectivity/bluetooth/transfer-data">Transferring data over BT</a>
 */
public class BluetoothConnection {
    private static final String TAG = "BluetoothConnection";

    private final Context context;
    private final LocalBroadcastManager localBcMgr;
    private MessageThread messageThread;

    public BluetoothConnection(Context context, BluetoothSocket socket, BluetoothDevice device) {
        this.context = context;
        this.localBcMgr = LocalBroadcastManager.getInstance(context);
        messageThread = new MessageThread(socket, device);
    }

    public void start() {
        messageThread.start();
    }

    public void cancel() {
        messageThread.cancel();
    }

    private class MessageThread extends Thread {
        private static final String TAG = "MessageThread";
        private final BluetoothSocket socket;
        private final BluetoothDevice device;
        private final InputStream inStream;
        private final OutputStream outStream;

        private byte[] readBuffer;

        public MessageThread(BluetoothSocket socket, BluetoothDevice device) {
            Intent intent = BluetoothMessage.ofConnectionStatusMessage(true, device).toIntent();
            localBcMgr.sendBroadcast(intent);

            this.socket = socket;
            this.device = device;
            InputStream tmpIn = null;
            OutputStream tmpOut = null;
            try {
                tmpIn = this.socket.getInputStream();
                tmpOut = this.socket.getOutputStream();
            } catch (IOException e) {
                e.printStackTrace();
            }
            this.inStream = tmpIn;
            this.outStream = tmpOut;

            this.readBuffer = new byte[BluetoothMessage.BUFFER_SIZE];
        }

        public void run() {
            Log.d(TAG, "MessageThread: Running.");
            boolean shldQuit = false;
            while (socket != null && !shldQuit) {
                shldQuit = read();
            }
        }

        public boolean read() {
            try {
                int bytes = inStream.read(readBuffer);
                String inMsg = new String(readBuffer, 0, bytes);
                Log.d(TAG, "InputStream: " + inMsg);

                StringBuilder strBuilder = new StringBuilder();
                strBuilder.append(inMsg);

                // find delimiter
                int delimiterIdx = strBuilder.indexOf("\n");
                if (delimiterIdx != -1) {
                    // build string and split by delimiter
                    String[] messages = strBuilder.toString().split("\n");
                    for (String message : messages) {
                        Intent intent = BluetoothMessage.ofStringMessage(message).toIntent();
                        localBcMgr.sendBroadcast(intent);

                    }
                }
            } catch (IOException e) {
                Log.e(TAG, "Error reading input stream. " + e.getMessage());
                Intent intent = BluetoothMessage.ofConnectionStatusMessage(false, device).toIntent();
                localBcMgr.sendBroadcast(intent);
                return true;
            }
            return false;
        }

        public void write(byte[] bytes) {
            try {
                outStream.write(bytes);
            } catch (IOException e) {
                Log.e(TAG, "Error writing to output stream. " + e.getMessage());
            }
        }

        public void cancel() {
            Log.d(TAG, "MessageThread: Socket closed.");
            try {
                socket.close();
            } catch (IOException e) {
                Log.e(TAG, "Could not close the MessageThread socket", e);
            }
            this.interrupt();
        }
    }

    public void sendMessage(String s) {
        Log.d(TAG, "write: Writing to output stream: " + s);
        messageThread.write(s.getBytes(StandardCharsets.UTF_8));
    }
 }
