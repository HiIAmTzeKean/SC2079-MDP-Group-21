ifconfig
sudo arp-scan --interface=en0 --localnet
> 192.168.2.53
> D8:3A:DD:4A:AC:6D


## within RPI
sudo apt-get update
sudo apt-get upgrade
# for wifi access point
sudo apt-get install hostapd
# for dhcp server
sudo apt-get install dnsmasq

sudo raspi-config

# create access point
sudo vim /etc/hostapd/hostapd.conf
    interface=wlan0
    driver=nl80211
    ssid=MDPGrp21
    wpa_passphrase=MDPGrp21
    hw_mode=g
    channel=8
    country_code=SG
    ieee80211n=1
    ieee80211d=1
    wmm_enabled=0
    macaddr_acl=0
    auth_algs=1
    ignore_broadcast_ssid=0
    wpa=2
    wpa_key_mgmt=WPA-PSK
    wpa_pairwise=CCMP TKIP
    rsn_pairwise=CCMP

    # 5G
    hw_mode=a
    channel=36
    country_code=US
    ieee80211d=1
    ieee80211n=1
    ieee80211ac=1
    wmm_enabled=1

sudo /usr/sbin/hostapd /etc/hostapd/hostapd.conf

sudo systemctl unmask hostapd
sudo systemctl enable hostapd
sudo systemctl start hostapd
sudo service hostapd start

# set up wireless interface
# this is going to be the gateway for the devices connecting to the RPI
sudo vim /etc/dhcpcd.conf
    interface wlan0
    static ip_address=192.168.21.21/24
    nohook wpa_supplicant

# we use 192.168.21.21/24 as our subnet
sudo vim /etc/dnsmasq.conf
    interface=wlan0
    bind-dynamic
    domain-needed
    bogus-priv
    dhcp-range=192.168.21.21,192.168.21.50,255.255.255.0,24h
    dhcp-option=option:dns-server, 8.8.8.8
# dhcp-range=192.168.10.10,192.168.10.50,12h defines a range of 40 available address leases, with a
# lease time of 12 hours. This range must not include your Dnsmasq server. You may define the lease time in seconds, minutes, or hours.

sudo systemctl start dnsmasq

# IP forwarding
sudo sh -c "echo 1 > /proc/sys/net/ipv4/ip_forward"

https://www.raspberryconnect.com/projects/65-raspberrypi-hotspot-accesspoints/168-raspberry-pi-hotspot-access-point-dhcpcd-method


sudo vim /etc/systemd/system/dbus-org.bluez.service
    ExecStartPost=/usr/bin/sdptool add SP

sudo vim /etc/systemd/system/rfcomm.service
    [Unit]
    Description=RFCOMM service
    After=bluetooth.service
    Requires=bluetooth.service

    [Service]
    ExecStart=/usr/bin/rfcomm listen /dev/rfcomm0 1

    [Install]
    WantedBy=multi-user.target

# scan for devices
sudo hcitool scan
# make rpi discoverable
sudo service bluetooth start
sudo hciconfig hci0 piscan

## File "/home/rpi21/.local/lib/python3.9/site-packages/bluetooth/bluez.py", line 271, in advertise_service
##     _bt.sdp_advertise_service (sock._sock, name, service_id, \
## _bluetooth.error: (13, 'Permission denied')
-> sudo chmod o+rw /var/run/sdp

# install python3.10
wget https://www.python.org/ftp/python/3.10.9/Python-3.10.9.tgz
sudo apt update
sudo apt-get install build-essential checkinstall -y
sudo apt install -y build-essential tk-dev libncurses5-dev libncursesw5-dev libreadline6-dev libdb5.3-dev libgdbm-dev libsqlite3-dev libssl-dev libbz2-dev libexpat1-dev liblzma-dev zlib1g-dev libffi-dev
tar -xzvf Python-3.10.9.tgz 
cd Python-3.10.9/
./configure --enable-optimizations
sudo make -j4 altinstall
sudo update-alternatives --install /usr/bin/python3 python3 /usr/local/bin/python3.10 1
sudo update-alternatives --config python3
sudo apt-get install python3-dev cmake -y
sudo apt-get install libbluetooth-dev
python3 -m pip install --upgrade pip
python3 -m pip install wheel setuptools pip --upgrade

sudo apt install -y gcc g++ gfortran libopenblas-dev liblapack-dev pkg-config python3-pip python3-dev
python3 -m pip install numpy
sudo apt-get install python-picamera python3-picamera

# Install OpenCV
cd ~
wget -O opencv.zip https://github.com/Itseez/opencv/archive/3.3.0.zip
unzip opencv.zip
wget -O opencv_contrib.zip https://github.com/Itseez/opencv_contrib/archive/3.3.0.zip
unzip opencv_contrib.zip

cd ~/opencv-3.3.0/
mkdir build
cd build
cmake -D CMAKE_BUILD_TYPE=RELEASE \
-D CMAKE_INSTALL_PREFIX=/usr/local \
-D INSTALL_PYTHON_EXAMPLES=ON \
-D OPENCV_EXTRA_MODULES_PATH=~/opencv_contrib-3.3.0/modules \
-D BUILD_EXAMPLES=ON ..

sudo vim /etc/dphys-swapfile
sudo /etc/init.d/dphys-swapfile stop
sudo /etc/init.d/dphys-swapfile start
make -j4



sudo ps -aux | grep rfcomm
sudo kill -9 <insert pid>


rfcomm_pid=$(ps -aux | grep '[r]fcomm' | awk '{print $2}')

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