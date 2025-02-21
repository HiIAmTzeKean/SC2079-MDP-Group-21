package com.mdp25.forever21.bluetooth;

import android.annotation.SuppressLint;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothSocket;
import android.content.Context;
import android.content.Intent;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import android.widget.Toast;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;

/**
 * Class responsible for the thread handling incoming/outgoing messages.
 * <p> Note that the messages are assumed to be strings.
 * <p> Reference: <a href="https://developer.android.com/develop/connectivity/bluetooth/transfer-data">Transferring data over BT</a>
 */
public class BluetoothConnection {
    private static final String TAG = "BluetoothConnection";

    public static final int READ_BUF_SIZE = 1024;
    public final static String ACTION_MSG_READ = BluetoothConnection.class.getPackageName() + "." + BluetoothConnection.class.getName() + ".ACTION_MSG_READ";
    public final static String EXTRA_MSG_READ = "EXTRA_MSG_READ";
    public final static String ACTION_CONNECTED = BluetoothConnection.class.getPackageName() + "." + BluetoothConnection.class.getName() + ".ACTION_CONNECTED";
    /** Boolean value, false for disconnected */
    public final static String EXTRA_CONNECTED = "EXTRA_CONNECTED";
    /** Equivalent to {@link BluetoothDevice#EXTRA_DEVICE } */
    public final static String EXTRA_DEVICE = BluetoothDevice.EXTRA_DEVICE;

    private final Context appContext;
    private final MessageThread messageThread;

    public BluetoothConnection(Context context, BluetoothSocket socket, BluetoothDevice device) {
        this.appContext = context.getApplicationContext(); // just in case
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

        private final byte[] readBuffer;

        private final Handler handler; // to post to main thread


        @SuppressLint("MissingPermission")
        public MessageThread(BluetoothSocket socket, BluetoothDevice device) {
            handler = new Handler(Looper.getMainLooper());

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

            this.readBuffer = new byte[READ_BUF_SIZE];

            handler.post(() -> {
                connectedBroadcast(true, device);
            });
        }

        @SuppressLint("MissingPermission")
        public void run() {
            Log.d(TAG, "MessageThread: Running.");
            boolean shldQuit = false;
            while (socket != null && !shldQuit) {
                shldQuit = read();
            }
            handler.post(() -> {
                connectedBroadcast(false, device);
                cancel(); // close the socket
            });
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
                String builtStr = strBuilder.toString();
                if (delimiterIdx != -1) {
                    // build string and split by delimiter
                    String[] messages = builtStr.split("\n");
                    Log.d(TAG, "Sending broadcast.");
                    readMsgBroadcast(messages);
                } else {
                    readMsgBroadcast(new String[]{builtStr});
                }
            } catch (IOException e) {
                Log.e(TAG, "Error reading input stream. " + e.getMessage());
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

        // sends the received message and broadcast it on main thread
        void readMsgBroadcast(String[] messages) {
            handler.post(() -> {
                for (String message : messages) {
                    Intent intent = new Intent(ACTION_MSG_READ)
                            .setPackage(appContext.getPackageName())
                            .putExtra(EXTRA_MSG_READ, message);
                    appContext.sendBroadcast(intent);
                }
            });
        }

        void connectedBroadcast(boolean connected, BluetoothDevice device) {
            handler.post(() -> {
                Intent intent = new Intent(ACTION_CONNECTED)
                        .setPackage(appContext.getPackageName())
                        .putExtra(EXTRA_CONNECTED, connected)
                        .putExtra(EXTRA_DEVICE, device);
                appContext.sendBroadcast(intent);
            });
        }
    }

    public void sendMessage(String s) {
        if (messageThread != null) {
            Log.d(TAG, "write: Writing to output stream: " + s);
            messageThread.write(s.getBytes(StandardCharsets.UTF_8));
        }
    }
}
