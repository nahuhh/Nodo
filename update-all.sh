#!/bin/bash
# Just a root wrapper for the update scripts. Bit silly, I know

#shellcheck source=home/nodo/common.sh
. /home/nodo/common.sh

bash /home/nodo/update-nodo.sh
cd /home/nodo || exit 1
chown nodo:nodo -R nodoui monero monero-lws p2pool xmrig onion-monero-block-explorer
mkdir -p /home/nodo/bin
chown nodo:nodo /home/nodo/bin
sudo -u nodo bash /home/nodo/update-monero.sh
sudo -u nodo bash /home/nodo/update-monero-lws.sh
sudo -u nodo bash /home/nodo/update-p2pool.sh
sudo -u nodo bash /home/nodo/update-xmrig.sh
sudo -u nodo bash /home/nodo/update-explorer.sh
sudo -u nodo bash /home/nodo/update-nodoui.sh
sudo -u nodo bash /home/nodo/update-pay.sh

# Restart services afterwards,
# otherwise the device would be nothing more than a very warm brick
services-stop

services-start
