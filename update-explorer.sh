#!/bin/bash

#shellcheck source=home/nodo/common.sh
. /home/nodo/common.sh
cd /home/nodo || exit 1

OLD_VERSION_EXP="${1:-$(getvar "versions.exp")}"

RELEASE="$(curl -fs https://raw.githubusercontent.com/MoneroNodo/Nodo/master/release-exp.txt)"

if [ -z "$RELEASE" ] && [ -z "$FIRSTINSTALL" ]; then # Release somehow not set or empty
	showtext "Failed to check for update for Monero Explorer"
	exit 0
fi

if [ "$RELEASE" == "$OLD_VERSION_EXP" ]; then
	showtext "No update for Monero Explorer"
	exit 0
fi

touch "$DEBUG_LOG"

showtext "
####################
Start setup-update-explorer.sh script $(date)
####################
"


#(1) Define variables and updater functions

showtext "Building Monero Blockchain Explorer..."

{
	tries=0
	until git clone -b master https://github.com/moneroexamples/onion-monero-blockchain-explorer.git; do
		sleep 1
		tries=$((tries + 1))
		if [ $tries -ge 5 ]; then
			exit 1
		fi
	done
	cd onion-monero-blockchain-explorer || exit
	mkdir build
	cd build || exit
	cmake -DMONERO_DIR=/home/nodo/monero --fresh ..
	make -j"$(nproc --ignore=2)" || exit 1
	cp xmrblocks /home/nodo/bin/ || exit 1
	chmod a+x /home/nodo/bin/xmrblocks || exit 1
	putvar "versions.exp" "$RELEASE" || exit 1
	cd || exit
	rm -rf /home/nodo/onion-monero-blockchain-explorer
} 2>&1 | tee -a "$DEBUG_LOG"

#
##End debug log
showtext "
####################
End setup-update-explorer.sh script $(date)
####################"
