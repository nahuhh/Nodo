#!/bin/bash
#(1) Define variables and updater functions
#shellcheck source=home/nodo/common.sh
. /home/nodo/common.sh
OLD_VERSION_LWS="${1:-$(getvar "versions.embeddedui")}"

RELEASE="$(curl -fs https://raw.githubusercontent.com/MoneroNodo/Nodo/master/release-embeddedui.txt)"
#RELEASE="release-v0.18" # TODO remove when live

if [ -z "$RELEASE" ]; then # Release somehow not set or empty
	showtext "Failed to check for update for LWS"
	exit 0
fi

if [ "$RELEASE" == "$OLD_VERSION_LWS" ]; then
	showtext "No update for LWS"
	exit 0
fi

touch "$DEBUG_LOG"

showtext "
####################
Start setup-update-embeddedui.sh script $(date)
####################
"

##Delete old version
showtext "Delete old version"
rm -rf /home/nodo/embeddedui 2>&1 | tee -a "$DEBUG_LOG"
showtext "Downloading Embedded UI"
{
	git clone --recursive https://github.com/moneronodo/embeddedui.git
	cd embeddedui || exit 1
	git checkout master
	git pull
	mkdir build
	cd build || exit 1
	showtext "Building Embedded UI"
	bash install.sh && putvar "versions.embeddedui" "$RELEASE"
} 2>&1 | tee -a "$DEBUG_LOG"
cd || exit 1
#Update system reference current LWS version number to New version number

##End debug log
showtext "Embedded UI Updated
####################
End setup-update-embeddedui.sh script $(date)
####################"
