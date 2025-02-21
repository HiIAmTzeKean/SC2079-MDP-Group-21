rfcomm_pid=$(ps -aux | grep 'rfcomm' | awk '{print $2}')

# Check if the PID was found
if [ -z "$rfcomm_pid" ]; then
    echo "rfcomm process not found."
else
    echo "rfcomm process found with PID: $rfcomm_pid"
    # Kill the rfcomm process
    sudo kill -9 "$rfcomm_pid"
    echo "rfcomm process with PID $rfcomm_pid has been killed."
fi
sudo systemctl start rfcomm
sudo rfcomm listen /dev/rfcomm0 1