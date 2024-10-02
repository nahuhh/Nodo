#!/bin/bash

##Open Sources:
# Web-UI by designmodo Flat-UI free project at https://github.com/designmodo/Flat-UI
# Monero github https://github.com/moneroexamples/monero-compilation/blob/master/README.md
# Monero Blockchain Explorer https://github.com/moneroexamples/onion-monero-blockchain-explorer
# MoneroNodo scripts and custom files at my repo https://github.com/shermand100/pinode-xmr
# PiVPN - OpenVPN server setup https://github.com/pivpn/pivpn

if [ ! "$EUID" = 0 ]; then
	printf '!! %s' "Please run as root"
	exit 1
fi

_cwd="$(pwd)"

#shellcheck source=home/nodo/common.sh
. "$_cwd"/home/nodo/common.sh
if check_connection; then
	showtext "Internet working fine -- starting installer"
else
	showtext "NO CONNECTION -- aborting!"
	exit 1
fi

##Create new user 'nodo'
showtext "Creating user 'nodo'..."
adduser --gecos "" --disabled-password --home /home/nodo nodo
chmod a+rx /home/nodo
usermod -a -G sudo nodo
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

showtext "setup-nodo.sh..."
bash "$_cwd"/setup-nodo.sh

bash "$_cwd"/home/nodo/setup-drive.sh "${_cwd}"

showtext "Setting up Monero..."
# Install monero for the first time
(
	cd /home/nodo || exit 1

	export FIRSTINSTALL=1
	mkdir -p /home/nodo/bin
	chown nodo:nodo /home/nodo/bin
	chmod a+rx /home/nodo/bin

	cd || exit
	git clone https://github.com/MoneroNodo/mesa
	cd mesa || exit
	sudo -u nodo bash ./install_mesa.sh

	showtext "Setting up Monero Daemon"
	sudo -u nodo bash /home/nodo/update-monero.sh

	showtext "Setting up Block Explorer"
	sudo -u nodo bash /home/nodo/update-explorer.sh

	showtext "Setting up Monero LWS"
	sudo -u nodo bash /home/nodo/update-monero-lws.sh

	showtext "Setting up XMRig"
	sudo -u nodo bash /home/nodo/update-xmrig.sh

	showtext "Setting up Nodo UI"
	sudo -u nodo bash /home/nodo/update-nodoui.sh

	showtext "Setting up Moneropay"
	sudo -u nodo bash /home/nodo/update-pay.sh

)
showtext "Start services"

systemctl daemon-reload
systemctl enable --now tor i2pd apparmor
systemctl enable --now monerod block-explorer monero-lws webui

services-start
sleep 3
swapfile=/media/monero/swap
sleep 1
showtext "Setting up swap on $swapfile"
dd if=/dev/zero of="$swapfile" bs=1M count=1024 conv=sync
mkswap "$swapfile"
printf '%s none swap defaults 0 0' "$swapfile" | tee -a /etc/fstab
swapon "$swapfile"

putvar 'i2p_address' $(printf "%s.b32.i2p" "$(head -c 391 /var/lib/i2pd/nasXmr.dat | sha256sum | xxd -r -p | base32 | sed s/=//g | tr A-Z a-z)")
putvar 'i2p_b32_addr_rpc' $(printf "%s.b32.i2p" "$(head -c 391 /var/lib/i2pd/nasXmrRpc.dat | sha256sum | xxd -r -p | base32 | sed s/=//g | tr A-Z a-z)")
putvar 'tor_address' "$(cat /var/lib/tor/hidden_service/hostname)"

## Install complete
showtext "Installation Complete"
