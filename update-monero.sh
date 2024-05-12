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
RELEASE=$(get_release_commit "monero-project" "monero")
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
	# first install monero dependencies
	git clone --recursive https://github.com/monero-project/monero.git

	cd monero/ || exit 1
	git reset --hard HEAD
	git pull --rebase
	git checkout "$RELEASE"
	git submodule update --init --force
	USE_DEVICE_TREZOR=OFF USE_SINGLE_BUILDDIR=1 make -j"$(nproc --ignore=2)" && \
		cp build/release/bin/monero* /home/nodo/bin/ && \
		chmod a+x /home/nodo/bin/monero* &&	\
		putvar "versions.monero" "$RELEASE"
} 2>&1 | tee -a "$DEBUG_LOG"

# {
# wget --no-verbose --show-progress --progress=dot:giga -O arm64 https://downloads.getmonero.org/arm64
# mkdir dl
# tar -xjvf arm64 -C dl
# mv dl/*/monero* /usr/bin/
# chmod a+x /usr/bin/monero*
# } 2>&1 | tee -a "$DEBUG_LOG"

#Update system version number
# putvar "versions.monero" "$RELEASE"
#cleanup old version number file

##End debug log
log "Monero Update Complete
####################
End setup-update-monero.sh script $(date)
####################"
