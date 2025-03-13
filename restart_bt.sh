rfcomm_pids=$(ps -aux | grep '[r]fcomm' | awk '{print $2}')

if [ -z "$rfcomm_pids" ]; then
    echo "rfcomm process not found."
else
    echo "rfcomm process found with PIDs: $rfcomm_pids"
    for pid in $rfcomm_pids; do
        sudo kill -9 "$pid"
        echo "rfcomm process with PID $pid has been killed."
    done
fi

# sudo systemctl start rfcomm
# sudo rfcomm listen /dev/rfcomm0 1