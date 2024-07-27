#!/bin/bash

#shellcheck source=home/nodo/common.sh
. /home/nodo/common.sh
cd /home/nodo || exit 1

OLD_VERSION_EXP="${1:-$(getvar "versions.pay")}"

RELEASE=$(gitlab_get_tag_commit "moneropay" "moneropay")

if [ -z "$RELEASE" ] && [ -z "$FIRSTINSTALL" ]; then # Release somehow not set or empty
	showtext "Failed to check for update for MoneroPay"
	exit 0
fi

if [ "$RELEASE" == "$OLD_VERSION_EXP" ]; then
	showtext "No update for MoneroPay"
	exit 0
fi

touch "$DEBUG_LOG"

showtext "Building Monero Blockchain Explorer..."

{
	git clone -b master https://gitlab.com/moneropay/moneropay/
	cd moneropay || exit
	git reset --hard HEAD
	git pull --rebase
	go build -o moneropay cmd/moneropay/main.go && \
		putvar "versions.exp" "$RELEASE" && \
		cp moneropay /home/nodo/bin/
} 2>&1 | tee -a "$DEBUG_LOG"
