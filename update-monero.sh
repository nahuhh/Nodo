#!/bin/bash

#shellcheck source=home/nodo/common.sh
. /home/nodo/common.sh

cd /home/nodo || exit 1

OLD_VERSION="${1:-$(getvar "versions.monero")}"
#Error Log:
touch "$DEBUG_LOG"
echo "
####################
Start update-monero.sh script $(date)
####################
" 2>&1 | tee -a "$DEBUG_LOG"

#Download variable for current monero release version
#FIXME: change url
# wget -q https://raw.githubusercontent.com/monero-ecosystem/PiNode-XMR/master/release.sh -O /home/nodo/release.sh
RELEASE="$(curl -fs https://raw.githubusercontent.com/MoneroNodo/Nodo/master/release-monero.txt)"
# RELEASE="release-v0.18" # TODO remove when live

if [ -z "$RELEASE" ]; then # Release somehow not set or empty
	showtext "Failed to check for update for Monero"
	exit 0
fi

if [ "$RELEASE" == "$OLD_VERSION" ]; then
	showtext "No update for Monero"
	exit 0
fi

showtext "Building Monero..."

{
	# first install monero dependancies
	git clone --recursive -b "$RELEASE" https://github.com/monero-project/monero.git
	git reset --hard HEAD

	cd monero/ || exit 1
	git pull
	USE_SINGLE_BUILDDIR=1 make && cp build/release/bin/monero* /usr/bin/ && chmod a+x /usr/bin/monero*
} 2>&1 | tee -a "$DEBUG_LOG"

# {
# wget --no-verbose --show-progress --progress=dot:giga -O arm64 https://downloads.getmonero.org/arm64
# mkdir dl
# tar -xjvf arm64 -C dl
# mv dl/*/monero* /usr/bin/
# chmod a+x /usr/bin/monero*
# } 2>&1 | tee -a "$DEBUG_LOG"

#Update system version number
putvar "versions.monero" "$RELEASE"
#cleanup old version number file

##End debug log
log "Monero Update Complete
####################
End setup-update-monero.sh script $(date)
####################"
