#!/bin/bash

#shellcheck source=home/nodo/common.sh
. /home/nodo/common.sh
cd /home/nodo || exit 1

OLD_VERSION_XMRIG="${1:-$(getvar "versions.xmrig")}"

RELEASE="$(curl -fs https://raw.githubusercontent.com/MoneroNodo/Nodo/master/release-xmrig.txt)"
#RELEASE="release-v0.18" # TODO remove when live

if [ -z "$RELEASE" ]; then # Release somehow not set or empty
	showtext "Failed to check for update for Monero xmrig"
	exit 0
fi

if [ "$RELEASE" == "$OLD_VERSION_XMRIG" ]; then
	showtext "No update for Monero xmrig"
	exit 0
fi

touch "$DEBUG_LOG"

showtext "
####################
Start setup-update-xmrig.sh script $(date)
####################
"


#(1) Define variables and updater functions

rm -rf /home/nodo/xmrig/
showtext "Building Monero xmrig..."

{
	git clone -b master https://github.com/xmrig/xmrig.git
	cd xmrig || exit
	git pull
	mkdir build
	cd build || exit
	cmake ..
	make -j$(nproc --ignore=2) && cp xmrig /usr/bin/ && chmod a+x /usr/bin/xmrig
} 2>&1 | tee -a "$DEBUG_LOG"

putvar "versions.xmrig" "$RELEASE"
#
##End debug log
showtext "
####################
End setup-update-xmrig.sh script $(date)
####################"
