#!/bin/bash

#shellcheck source=home/nodo/common.sh
. /home/nodo/common.sh
cd /home/nodo || exit 1

OLD_VERSION_P2POOL="${1:-$(getvar "versions.p2pool")}"

RELEASE="$(curl -fs https://raw.githubusercontent.com/MoneroNodo/Nodo/master/release-p2pool.txt)"
#RELEASE="release-v0.18" # TODO remove when live

if [ -z "$RELEASE" ]; then # Release somehow not set or empty
	showtext "Failed to check for update for Monero p2pool"
	exit 0
fi

if [ "$RELEASE" == "$OLD_VERSION_P2POOL" ]; then
	showtext "No update for Monero p2pool"
	exit 0
fi

touch "$DEBUG_LOG"

showtext "
####################
Start update-p2pool.sh script $(date)
####################
"

rm -rf /home/nodo/p2pool/
showtext "Building Monero p2pool..."

{
	git clone --recursive -b master https://github.com/SChernykh/p2pool.git
	cd p2pool || exit
	git pull
	mkdir build
	cd build || exit
	cmake ..
	make -j$(nproc --ignore=2) && cp p2pool /usr/bin/ && chmod a+x /usr/bin/p2pool
} 2>&1 | tee -a "$DEBUG_LOG"

putvar "versions.p2pool" "$RELEASE"
#
##End debug log
showtext "
####################
End update-p2pool.sh script $(date)
####################"
