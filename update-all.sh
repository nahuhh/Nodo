#!/bin/bash
# Just a root wrapper for the update scripts. Bit silly, I know

#shellcheck source=home/nodo/common.sh
. /home/nodo/common.sh

UPD="$(jq -r '.config.autoupdate' /home/nodo/variables/config.json)"

if [ "$UPD" = "FALSE" ] && [ -z "$1" ]; then
	return 0
fi

bash /home/nodo/update-nodo.sh
cd /home/nodo || exit 1
chown nodo:nodo -R nodoui monero monero-lws xmrig onion-monero-block-explorer
mkdir -p /home/nodo/bin
chown nodo:nodo /home/nodo/bin
sudo -u nodo bash /home/nodo/update-monero.sh
sudo -u nodo bash /home/nodo/update-monero-lws.sh
sudo -u nodo bash /home/nodo/update-xmrig.sh
sudo -u nodo bash /home/nodo/update-explorer.sh
sudo -u nodo bash /home/nodo/update-pay.sh
sudo bash /home/nodo/update-nodoui.sh

# Restart services afterwards,
# otherwise the device would be nothing more than a very warm brick
services-stop

services-start
