#!/bin/bash

. ./common.sh

touch "$DEBUG_LOG"

echo "
####################
Start setup-update-explorer.sh script $(date)
####################
" 2>&1 | tee -a "$DEBUG_LOG"


#(1) Define variables and updater functions

{
	#Permission Setting
	chmod 755 /home/nanode/current-ver-exp.sh
	chmod 755 /home/nanode/exp-new-ver.sh
	#Load Variables
	. /home/nanode/current-ver-exp.sh
	. /home/nanode/exp-new-ver.sh
	#Load boot status - what condition was node last run
	. /home/nanode/bootstatus.sh
} 2>&1 | tee -a "$DEBUG_LOG"


#Stop Node to make system resources available.
{
services-stop
sudo systemctl stop blockExplorer.service
echo "Monero node stop command sent to make system resources available for update, allowing 30 seconds for safe shutdown"
echo "Deleting Old Version"
rm -rf /home/nanode/onion-monero-blockchain-explorer/ 2> >(tee -a "$DEBUG_LOG" >&2)
showtext "Building Monero Blockchain Explorer
*******************************************************
***This will take a few minutes - Hardware Dependent***
*******************************************************"
git clone -b master https://github.com/moneroexamples/onion-monero-blockchain-explorer.git 2> >(tee -a "$DEBUG_LOG" >&2)
cd onion-monero-blockchain-explorer || exit
mkdir build && cd build || exit
cmake .. 2> >(tee -a "$DEBUG_LOG" >&2)
make 2> >(tee -a "$DEBUG_LOG" >&2)
cd || exit
#Update system reference Explorer version number version number
echo "#!/bin/bash
CURRENT_VERSION_EXP=$NEW_VERSION_EXP" > /home/nanode/current-ver-exp.sh

services-start "$BOOT_STATUS"
} 2>&1 | tee -a "$DEBUG_LOG"

rm /home/nanode/new-ver-exp.sh 2> >(tee -a "$DEBUG_LOG" >&2)
#
##End debug log
echo "
####################
" 2>&1 | tee -a "$DEBUG_LOG"
log "End setup-update-explorer.sh script $(date)"
echo "
####################
" 2>&1 | tee -a "$DEBUG_LOG"
