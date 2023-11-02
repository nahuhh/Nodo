#!/bin/bash

##Open Sources:
# Web-UI by designmodo Flat-UI free project at https://github.com/designmodo/Flat-UI
# Monero github https://github.com/moneroexamples/monero-compilation/blob/master/README.md
# Monero Blockchain Explorer https://github.com/moneroexamples/onion-monero-blockchain-explorer
# MoneroNodo scripts and custom files at my repo https://github.com/shermand100/pinode-xmr
# PiVPN - OpenVPN server setup https://github.com/pivpn/pivpn

#shellcheck source=home/nodo/common.sh

_cwd=$PWD
test "$_cwd" = "" && exit 1

. "$_cwd"/home/nodo/common.sh
if check_connection; then
	showtext "Internet working fine -- starting installer"
else
	showtext "NO CONNECTION -- aborting!"
	exit 1
fi
systemctl disable --now gdm.service # no gnome-shell necessary

##Create new user 'nodo'
showtext "Creating user 'nodo'..."
adduser --gecos "" --disabled-password --home /home/nodo nodo
adduser --system --no-create-home --shell /bin/false --group monero

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

###Clone MoneroNodo to device from git
#showtext "Downloading MoneroNodo files..."
#git clone --single-branch https://github.com/MoneroNodo/Nodo.git 2>&1 | tee -a "$DEBUG_LOG"

#Stop Node to make system resources available.
services-stop

showtext "setup-nodo.sh..."
. "$_cwd"/setup-nodo.sh

showtext "Setting up Monero..."
# Install monero for the first time
(
	cd /home/nodo || exit 1

	showtext "Setting up Monero Daemon"
	# Install monero block explorer for the first time
	sudo -u nodo bash ./update-monero.sh

	showtext "Setting up Block Explorer"
	# Install monero block explorer for the first time
	sudo -u nodo bash ./update-explorer.sh

	showtext "Setting up Monero LWS"
	# Install monero block explorer for the first time
	sudo -u nodo bash ./update-monero-lws.sh

	showtext "Setting up P2Pool"
	# Install monero block explorer for the first time
	sudo -u nodo bash ./update-p2pool.sh

	showtext "Setting up XMRig"
	# Install monero block explorer for the first time
	sudo -u nodo bash ./update-xmrig.sh
)
## Install complete
showtext "Installation Complete"
