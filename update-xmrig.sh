#!/bin/bash

#shellcheck source=home/nodo/common.sh
. /home/nodo/common.sh
cd /home/nodo || exit 1

OLD_VERSION_XMRIG="${1:-$(getvar "versions.xmrig")}"

RELEASE=$(get_release_commit "xmrig" "xmrig")

if [ -z "$RELEASE" ] && [ -z "$FIRSTINSTALL" ]; then # Release somehow not set or empty
	showtext "Failed to check for update for Monero xmrig"
	exit 0
fi

if [ "$RELEASE" == "$OLD_VERSION_XMRIG" ]; then
	showtext "No update for Monero xmrig"
	exit 0
fi

touch "$DEBUG_LOG"

#(1) Define variables and updater functions

showtext "Building Monero xmrig..."

{
	git clone -b master https://github.com/xmrig/xmrig.git
	cd xmrig || exit
	git reset --hard HEAD
	git pull --rebase
	git checkout "$RELEASE"
	mkdir build
	cd build || exit
	cmake ..
	make -j"$(nproc --ignore=2)" || exit 1
	cp xmrig /home/nodo/bin/ || exit 1
	chmod a+x /home/nodo/bin/xmrig || exit 1
	putvar "versions.xmrig" "$RELEASE"
	cd || exit 1
	rm -rf /home/nodo/xmrig/
} 2>&1 | tee -a "$DEBUG_LOG"
