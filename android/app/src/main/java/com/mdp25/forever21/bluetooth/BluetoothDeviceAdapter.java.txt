package com.mdp25.forever21.bluetooth;

import android.annotation.SuppressLint;
import android.bluetooth.BluetoothDevice;
import android.content.Context;
import android.content.res.ColorStateList;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.core.content.ContextCompat;
import androidx.recyclerview.widget.RecyclerView;

import com.mdp25.forever21.R;

import java.util.Collection;
import java.util.List;
import java.util.function.Consumer;

/**
 * For use with a {@link RecyclerView}.
 */
public class BluetoothDeviceAdapter extends RecyclerView.Adapter<BluetoothDeviceAdapter.ViewHolder> {
    private List<BluetoothDeviceModel> devices;
    private Context context;
    private Consumer<BluetoothDeviceModel> onClickBtDevice;

    public BluetoothDeviceAdapter(Context context, List<BluetoothDeviceModel> devices, Consumer<BluetoothDeviceModel> onClickBtDevice) {
        this.context = context;
        this.devices = devices;
        this.onClickBtDevice = onClickBtDevice;
    }


    @NonNull
    @Override
    public ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(context).inflate(R.layout.item_bluetooth_device, parent, false);
        return new ViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull BluetoothDeviceAdapter.ViewHolder holder, int position) {
        BluetoothDeviceModel device = devices.get(position);

        holder.deviceName.setText(device.name() != null ? device.name() : "Unknown Device");
        holder.deviceAddress.setText(device.address());

        // Set different background for paired devices
        if (device.isPaired()) {
            //holder.itemView.setBackgroundTintList(ColorStateList.valueOf(ContextCompat.getColor(context, R.color.paired_device_bg)));
            holder.pairedStatus.setVisibility(View.VISIBLE);
        } else {
            //holder.itemView.setBackgroundTintList(ColorStateList.valueOf(ContextCompat.getColor(context, android.R.color.transparent)));
            holder.pairedStatus.setVisibility(View.GONE);
        }

        holder.itemView.setOnClickListener(v -> {
            if (onClickBtDevice != null) {
                onClickBtDevice.accept(device);
            }
        });
    }

    @Override
    public int getItemCount() {
        return devices.size();
    }


    @SuppressLint({"MissingPermission", "NotifyDataSetChanged"})
    public void initPairedDevices(Collection<BluetoothDevice> pairedDevices) {
        devices.clear();
        for (BluetoothDevice device : pairedDevices) {
            devices.add(new BluetoothDeviceModel(
                    device,
                    device.getName(),
                    device.getAddress(),
                    true
            ));
        }
        notifyDataSetChanged();
    }

    @SuppressLint({"MissingPermission"})
    public void addDiscoveredDevice(BluetoothDevice bluetoothDevice) {
        // check if device is not already in the list
        boolean deviceExists = false;
        for (BluetoothDeviceModel existingDevice : devices) {
            if (existingDevice.address().equals(bluetoothDevice.getAddress())) {
                deviceExists = true;
                break;
            }
        }
        if (!deviceExists) {
            int position = devices.size();
            devices.add(new BluetoothDeviceModel(
                    bluetoothDevice,
                    bluetoothDevice.getName(),
                    bluetoothDevice.getAddress(),
                    false
            ));
            notifyItemInserted(position);
        }
    }

    public static class ViewHolder extends RecyclerView.ViewHolder {
        TextView deviceName;
        TextView deviceAddress;
        TextView pairedStatus;

        public ViewHolder(@NonNull View itemView) {
            super(itemView);
            deviceName = itemView.findViewById(R.id.deviceName);
            deviceAddress = itemView.findViewById(R.id.deviceAddress);
            pairedStatus = itemView.findViewById(R.id.pairedStatus);
        }
    }
}
