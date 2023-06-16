# Login
User: nodo
Passwd: MoneroNodo


#That's it. Nodo up and running. Connect your GUI with IP you used above and
Port 18081. Interface is available from any device on your network at the IP you
used.

# ____________________________________________________________________________________________________


# For info on the build;


# Create `root` user and `nodo` user
# `root` and `nodo` set to 9WNN5FPAlsmUzyLZ


#set nodo sudo no password access in

sudo visudo

nodo   ALL = NOPASSWD: ALL

# Dependencies

apt-get install gdisk xfsprogs build-essential cmake pkg-config libssl-dev
libzmq3-dev libunbound-dev libsodium-dev libunwind8-dev liblzma-dev
libreadline6-dev libldns-dev libexpat1-dev libpgm-dev qttools5-dev-tools
libhidapi-dev libusb-1.0-0-dev libprotobuf-dev protobuf-compiler libudev-dev
libboost-chrono-dev libboost-date-time-dev libboost-filesystem-dev
libboost-locale-dev libboost-program-options-dev libboost-regex-dev
libboost-all-dev libboost-serialization-dev libboost-system-dev
libboost-thread-dev ccache doxygen graphviz -y

# crontab added - most are commands outputting to txt files for Web UI to read -
All run once per minute unless otherwise stated

root:
0 4 * * 1 /home/nodo/update-all.sh

nodo:
* * * * * /home/nodo/cpuTemp.sh
0 */4 * * * /home/nodo/df-h.sh
0 */4 * * * /home/nodo/printPl.sh
* * * * * /home/nodo/free-h.sh
* * * * * /home/nodo/system-monitor.sh
0 12 * * 7 /home/nodo/weekly-log-clean.sh

#UPDATER: Downloads
https://raw.githubusercontent.com/MoneroNodo/Nodo/master/release.txt
The updater script then compares this number with it's current version and only
if the new version number is higher it will pull from the repo and apply the
	updated files.
It will look for new versions for monerod, monero-onion-blockchain-explorer,
monero-lws, and build them respectively. It will then restart each service, so
a very short downtime (<10s) will occur.


# disabled ipv6 ( otherwise confused response from HOSTNAME command for IP
address )

echo 'net.ipv6.conf.all.disable_ipv6 = 1' | tee -a /etc/sysctl.conf
echo 'net.ipv6.conf.default.disable_ipv6 = 1' | tee -a /etc/sysctl.conf
echo 'net.ipv6.conf.lo.disable_ipv6 = 1' | tee -a /etc/sysctl.conf

ipv6.disable=1

# All services are handled by Systemd with dynamically generated run flags
(using `eval`) and configuration is handled by a json file at;

/home/nodo/variables/config.json

This json file can be edited through the web UI, or the display UI.

# UFW setup

ufw allow 80
ufw allow 443
ufw allow 18080
ufw allow 18081
ufw allow 4200
ufw allow 22
ufw enable

# Root ssh login disabled, only user 'nodo' allowed.
