#!/bin/bash

UPD="$(jq -r '.config.autoupdate.nodo' /home/nodo/variables/config.json)"

if [ "$UPD" = "FALSE" ] && [ -z "$1" ]; then
	return 0
fi

#(1) Define variables and updater functions
#shellcheck source=home/nodo/common.sh
. /home/nodo/common.sh
cd /home/nodo || exit 1
OLD_VERSION_EUI="${1:-$(getvar "versions.nodoui")}"


RELEASE=$(get_tag_commit "moneronodo" "nodoui")

if [ -z "$RELEASE" ] && [ -z "$FIRSTINSTALL" ]; then # Release somehow not set or empty
	showtext "Failed to check for update for Nodo UI"
	exit 0
fi

if [ "$RELEASE" == "$OLD_VERSION_EUI" ]; then
	showtext "No update for Nodo UI"
	exit 0
fi

touch "$DEBUG_LOG"

showtext "
####################
Start setup-update-nodoui.sh script $(date)
####################
"

##Delete old version
showtext "Delete old version"
showtext "Downloading Nodo UI"
{
	git clone --recursive https://github.com/moneronodo/nodoui.git
	cd nodoui || exit 1
	git reset --hard HEAD
	git checkout master
	git pull
	showtext "Building Nodo UI"
	bash ./install.sh || exit 1
	putvar "versions.nodoui" "$RELEASE" || exit 1
	cd || exit
	rm  -rf /home/nodo/nodoui
} 2>&1 | tee -a "$DEBUG_LOG"
cd || exit 1
##End debug log
showtext "Nodo UI Updated
####################
End setup-update-nodoui.sh script $(date)
####################"
