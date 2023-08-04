#!/bin/bash

##Open Sources:
# Web-UI by designmodo Flat-UI free project at https://github.com/designmodo/Flat-UI
# Monero github https://github.com/moneroexamples/monero-compilation/blob/master/README.md
# Monero Blockchain Explorer https://github.com/moneroexamples/onion-monero-blockchain-explorer
# MoneroNodo scripts and custom files at my repo https://github.com/shermand100/pinode-xmr
# PiVPN - OpenVPN server setup https://github.com/pivpn/pivpn

#shellcheck source=home/nodo/common.sh

_cwd=$(pwd)
test -z "$_cwd" && exit 1

. "${_cwd}"/home/nodo/common.sh
if check_connection; then
	showtext "Internet working fine -- starting installer"
else
	showtext "NO CONNECTION -- aborting!"
	exit 1
fi

##Create new user 'nodo'
showtext "Creating user 'nodo'..."
adduser nodo --disabled-password --gecos ""
adduser --system --no-create-home --shell /bin/false --group monero monero

#Set nodo password 'MoneroNodo'
echo "nodo:MoneroNodo" | chpasswd
echo "root:$(openssl rand -base64 48)" | chpasswd
showtext "nodo password changed to 'MoneroNodo'"

##Change system hostname to MoneroNodo
showtext "Changing system hostname to 'MoneroNodo'..."
echo 'MoneroNodo' | tee /etc/hostname
#sed -i '6d' /etc/hosts
echo '127.0.0.1       MoneroNodo' | tee -a /etc/hosts
hostname MoneroNodo

##Disable IPv6 (confuses Monero start script if IPv6 is present)
#and IPv6 sucks
showtext "Disabling IPv6..."
echo 'net.ipv6.conf.all.disable_ipv6 = 1' | tee -a /etc/sysctl.conf
echo 'net.ipv6.conf.default.disable_ipv6 = 1' | tee -a /etc/sysctl.conf
echo 'net.ipv6.conf.lo.disable_ipv6 = 1' | tee -a /etc/sysctl.conf

##Perform system update and upgrade now. This then allows for reboot before next install step, preventing warnings about kernal upgrades when installing the new packages (dependencies).
#setup debug file to track errors
showtext "Creating Debug log..."
touch "$DEBUG_LOG"
chown nodo "$DEBUG_LOG"
chmod 777 "$DEBUG_LOG"

#force confnew by default everywhere
echo "force-confnew" >/etc/dpkg/dpkg.cfg.d/force-confnew

##Update and Upgrade system
showtext "Downloading and installing OS updates..."
{
	apt-get update
	apt-get --yes upgrade
	apt-get --yes dist-upgrade
	apt-get upgrade -y
	##Auto remove any obsolete packages
	apt-get autoremove -y 2>&1 | tee -a "$DEBUG_LOG"
} 2>&1 | tee -a "$DEBUG_LOG"

###Begin2

##Update and Upgrade system (This step repeated due to importance and maybe someone using this installer script out-of-sequence)
showtext "Verifying Update..."
{
	apt-get update
	apt-get --yes upgrade
	apt-get --yes dist-upgrade
	apt-get upgrade -y
} 2>&1 | tee -a "$DEBUG_LOG"

##Installing dependencies for --- Web Interface
showtext "Installing dependencies for Web Interface..."
apt-get install apache2 shellinabox php php-common avahi-daemon -y 2>&1 | tee -a "$DEBUG_LOG"
usermod -a -G nodo www-data
##Installing dependencies for --- Monero
# showtext "Installing dependencies for --- Monero"
# apt-get update
apt-get install gdisk xfsprogs build-essential cmake pkg-config libssl-dev libzmq3-dev libunbound-dev libsodium-dev libunwind8-dev liblzma-dev libreadline6-dev libldns-dev libexpat1-dev libpgm-dev qttools5-dev-tools libhidapi-dev libusb-1.0-0-dev libprotobuf-dev protobuf-compiler libudev-dev libboost-chrono-dev libboost-date-time-dev libboost-filesystem-dev libboost-locale-dev libboost-program-options-dev libboost-regex-dev libboost-all-dev libboost-serialization-dev libboost-system-dev libboost-thread-dev ccache doxygen graphviz -y 2>&1 | tee -a "$DEBUG_LOG"

showtext "Install home contents"
cp -r "${_cwd}"/home/nodo/* /home/nodo/
cp -r "${_cwd}"/etc/* /etc/
cp -r "${_cwd}"/HTML/* /var/www/html/
chown httpd:httpd -R /var/www/html
cp "${_cwd}"/update-*sh /home/nodo/
chown nodo:nodo -R /home/nodo

log "manual build of gtest for --- Monero"
{
	cd /usr/src/gtest || exit 1
	apt-get install libgtest-dev -y
	cmake .
	make
	cp "${_cwd}"/libg* /usr/lib/
	cd || exit 1
} 2>&1 | tee -a "$DEBUG_LOG"

##Checking all dependencies are installed for --- miscellaneous (security tools-fail2ban-ufw, menu tool-dialog, screen, mariadb)
showtext "Checking all dependencies are installed..."
{
	apt-get install git mariadb-client mariadb-server screen fail2ban ufw dialog jq libcurl4-openssl-dev libpthread-stubs0-dev cron -y
	apt-get install exfat-fuse exfat-utils -y
} 2>&1 | tee -a "$DEBUG_LOG"
#libcurl4-openssl-dev & libpthread-stubs0-dev for block-explorer

##Clone MoneroNodo to device from git
showtext "Downloading MoneroNodo files..."
git clone --single-branch https://github.com/MoneroNodo/Nodo.git 2>&1 | tee -a "$DEBUG_LOG"

##Configure ssh security. Allows only user 'nodo'. Also 'root' login disabled via ssh, restarts config to make changes
showtext "Configuring SSH security..."
{
	# cp "${_cwd}"/etc/ssh/sshd_config /etc/ssh/sshd_config
	chmod 644 /etc/ssh/sshd_config
	chown root /etc/ssh/sshd_config
	systemctl restart sshd.service
} 2>&1 | tee -a "$DEBUG_LOG"
showtext "SSH security config complete"

##Copy MoneroNodo scripts to home folder
showtext "Moving MoneroNodo scripts into position..."
{
	cp "${_cwd}"/home/nodo/* /home/nodo/
	cp "${_cwd}"/home/nodo/.profile /home/nodo/
	chmod 777 -R /home/nodo/* #Read/write access needed by www-data to action php port, address customisation
} 2>&1 | tee -a "$DEBUG_LOG"
showtext "Success"

##Add MoneroNodo systemd services
showtext "Addding MoneroNodo systemd services..."
{
	# cp "${_cwd}"/etc/systemd/system/*.service /etc/systemd/system/
	chmod 644 /etc/systemd/system/*.service
	chown root /etc/systemd/system/*.service
	systemctl daemon-reload
	systemctl start moneroStatus.service
	systemctl enable moneroStatus.service
} 2>&1 | tee -a "$DEBUG_LOG"
showtext "Success"

showtext "Configuring apache server for access to Monero log file..."
{
	cp "${_cwd}"/etc/apache2/sites-enabled/000-default.conf /etc/apache2/sites-enabled/000-default.conf
	chmod 777 /etc/apache2/sites-enabled/000-default.conf
	chown root /etc/apache2/sites-enabled/000-default.conf
	/etc/init.d/apache2 restart
} 2>&1 | tee -a "$DEBUG_LOG"

showtext "Success"

##Setup local hostname
showtext "Setting up local hostname..."
{
	cp "${_cwd}"/etc/avahi/avahi-daemon.conf /etc/avahi/avahi-daemon.conf
	/etc/init.d/avahi-daemon restart
} 2>&1 | tee -a "$DEBUG_LOG"

showtext "Setting up SSD..."

bash ./setup-drive.sh

##Install log.io (Real-time service monitoring)
#Establish Device IP
DEVICE_IP=$(getip)
showtext "Installing log.io..."

{
	apt-get install nodejs npm -y
	npm install -g log.io
	npm install -g log.io-file-input
	mkdir -p ~/.log.io/inputs/
	cp "${_cwd}"/.log.io/inputs/file.json ~/.log.io/inputs/file.json
	cp "${_cwd}"/.log.io/server.json ~/.log.io/server.json
	sed -i "s/127.0.0.1/$DEVICE_IP/g" ~/.log.io/server.json
	sed -i "s/127.0.0.1/$DEVICE_IP/g" ~/.log.io/inputs/file.json
	systemctl start log-io-server.service
	systemctl start log-io-file.service
	systemctl enable log-io-server.service
	systemctl enable log-io-file.service
} 2>&1 | tee -a "$DEBUG_LOG"

#Install webui
showtext "Installing python dependencies..."

{
	mkdir /home/nodo/webui
	chown nodo /home/nodo/webui
	chmod gu+rx nodo:nodo /home/nodo/webui
	cd /home/nodo/webui || return 1
	apt-get install -y software-properties-common
	apt-get install -y python3.8 python3.8-dev python-pip python-virtualenv
	add-apt-repository -y ppa:deadsnakes/ppa
	virtualenv --python=python3.8 venv
	(
		. venv/bin/activate
		venv/bin/pip3.11 install Cython
		venv/bin/pip3.11 install numpy
		venv/bin/pip3.11 install dash
		venv/bin/pip3.11 install dash_bootstrap_components dash_mantine_components dash_iconify
		venv/bin/pip3.11 install pandas
		venv/bin/pip3.11 install dash_breakpoints dash_daq
		venv/bin/pip3.11 install furl
		venv/bin/pip3.11 install psutil
	)
} 2>&1 | tee -a "$DEBUG_LOG"

##Install crontab
showtext "Setting up crontab..."
crontab -u nodo var/spool/cron/crontabs/nodo 2>&1 | tee -a "$DEBUG_LOG"
crontab -u root var/spool/cron/crontabs/root 2>&1 | tee -a "$DEBUG_LOG"
showtext "Success"

##End debug log
{
	showtext "
	####################
	End ubuntu-install-continue.sh script $(date)
	####################"
} 2>&1 | tee -a "$DEBUG_LOG"

#Stop Node to make system resources available.
services-stop

showtext "Downloading Monero..."
# Install monero for the first time
sudo -u nodo bash ./update-monero.sh

showtext "Downloading Block Explorer..."
# Install monero block explorer for the first time
sudo -u nodo bash ./update-explorer.sh

showtext "Downloading Monero LWS"
# Install monero block explorer for the first time
sudo -u nodo bash ./update-lws.sh

showtext "Downloading Monero LWS"
# Install monero block explorer for the first time
sudo -u nodo bash ./update-lws-admin.sh
putvar 'lws_admin_key' "$(uuidgen -r)"

ufw allow 80
ufw allow 443
ufw allow 18080
ufw allow 18081
ufw allow 18083
ufw allow 4200
ufw allow 22
ufw enable

services-start

showtext "Start services"
systemctl daemon-reload
systemctl enable --now monerod.service
systemctl enable --now webui.service

## Install complete
showtext "Installation Complete"
