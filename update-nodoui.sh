#!/bin/bash
#(1) Define variables and updater functions
#shellcheck source=home/nodo/common.sh
. /home/nodo/common.sh
OLD_VERSION_EUI="${1:-$(getvar "versions.nodoui")}"


RELEASE=$(get_tag_commit "moneronodo" "nodoui")
#RELEASE="release-v0.18" # TODO remove when live

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
rm -rf /home/nodo/nodoui 2>&1 | tee -a "$DEBUG_LOG"
showtext "Downloading Nodo UI"
{
	git clone --recursive https://github.com/moneronodo/nodoui.git
	cd nodoui || exit 1
	git checkout master
	git pull
	showtext "Building Nodo UI"
	bash ./install.sh && putvar "versions.nodoui" "$RELEASE"
} 2>&1 | tee -a "$DEBUG_LOG"
cd || exit 1
##End debug log
showtext "Nodo UI Updated
####################
End setup-update-nodoui.sh script $(date)
####################"
