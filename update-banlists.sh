#!/bin/bash

. "$_cwd"/home/nodo/common.sh

cd /media/monero/ || exit 1
{
	[ "$(getvar "banlists.boog900")" == "TRUE" ] && curl -LSs https://github.com/Boog900/monero-ban-list/raw/refs/heads/main/ban_list.txt
	[ "$(getvar "banlists.gui-xmr-pm")" == "TRUE" ] && curl -LSs https://gui.xmr.pm/files/block.txt
} | sort -u > newbanlist && cp newbanlist banlist.txt

chown monero:monero banlist.txt
chmod 600 banlist.txt
