package com.mdp25.forever21.bluetooth;

import android.bluetooth.BluetoothDevice;
import android.content.Intent;
import android.os.Parcel;
import android.os.Parcelable;

import androidx.annotation.NonNull;

import java.util.Objects;

/**
 * Represents a bluetooth message sent to/from the robot.
 * <p> Use {@code ofXXX()} to create the subclassed record.
 * TODO not yet used
 */
public sealed interface BluetoothMessage extends Parcelable permits BluetoothMessage.CustomMessage, BluetoothMessage.StatusMessage, BluetoothMessage.StringMessage {
    // this class uses the sealed..permit feature as a usage example, not strictly necessary

    public final static int BUFFER_SIZE = 1024;
    public final static String INTENT_ACTION = "BluetoothMessage";
    public final static String INTENT_EXTRA_NAME = "msg";

    @Override
    public default int describeContents() {
        return 0;
    }

    /**
     * Use this method to quickly create an Intent with {@link Intent#putExtra(String, Parcelable)} on this.
     */
    public default Intent toIntent() {
        Intent ret = new Intent(INTENT_ACTION);
        ret.putExtra(INTENT_EXTRA_NAME, this);
        return ret;
    }

    /**
     * Sister method to {@link #toIntent()}.
     * @param intent from {@link #toIntent()}
     */
    public static BluetoothMessage fromIntent(Intent intent) {
        if (!Objects.equals(intent.getAction(), INTENT_ACTION)) {
            throw new IllegalArgumentException("This intent's action does not match. Is this intent from BluetoothMessage.toIntent?");
        }
        return intent.getParcelableExtra(INTENT_EXTRA_NAME, BluetoothMessage.class);
    }

    //TODO, add more based on reqs

    public static BluetoothMessage ofConnectionStatusMessage(boolean connected, BluetoothDevice device) {
        return new StatusMessage(connected, device);
    }

    public static BluetoothMessage ofStringMessage(String str) {
        return new StringMessage(str);
    }

    public static record StatusMessage(boolean connected, BluetoothDevice device) implements BluetoothMessage {
        public static final Parcelable.Creator<StatusMessage> CREATOR = new Parcelable.Creator<>() {
            public StatusMessage createFromParcel(Parcel in) {
                return new StatusMessage(in.readBoolean(), in.readParcelable(BluetoothDevice.class.getClassLoader(), BluetoothDevice.class));
            }

            public StatusMessage[] newArray(int size) {
                return new StatusMessage[size];
            }
        };
        @Override
        public void writeToParcel(@NonNull Parcel parcel, int flags) {
            parcel.writeBoolean(connected);
            parcel.writeParcelable(device, flags);
        }
    }

    public static record StringMessage(String str) implements BluetoothMessage {
        public static final Parcelable.Creator<StringMessage> CREATOR = new Parcelable.Creator<>() {
            public StringMessage createFromParcel(Parcel in) {
                return new StringMessage(in.readString());
            }

            public StringMessage[] newArray(int size) {
                return new StringMessage[size];
            }
        };
        @Override
        public void writeToParcel(@NonNull Parcel parcel, int flags) {
            parcel.writeString(str);
        }
    }



    /**
     * This non-sealed class is provided for future extension.
     */
    public abstract non-sealed class CustomMessage implements BluetoothMessage {}

}
