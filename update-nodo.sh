#!/bin/bash
#Create/ammend debug file for handling update errors:
#shellcheck source=home/nodo/common.sh
. /home/nodo/common.sh
cd /root/moneronodo || exit 1
OLD_VERSION_NODO="${1:-$(getvar "versions.nodo")}"
touch "$DEBUG_LOG"
echo "
####################
Start update-nodo.sh script $(date)
####################
" | tee -a "$DEBUG_LOG"

RELEASE="$(curl -fs https://raw.githubusercontent.com/MoneroNodo/Nodo/master/release.txt)"
#RELEASE="alpha" # TODO remove when live

if [ -z "$RELEASE" ]; then # Release somehow not set or empty
	showtext "Failed to check for update for Nodo"
	exit 0
fi

if [ "$RELEASE" == "$OLD_VERSION_NODO" ]; then
	showtext "No update for Nodo"
	exit 0
fi

_cwd=/root/nodo
test -z "$_cwd" && exit 1
cd "${_cwd}" || exit 1

git reset --hard HEAD
git pull

##Update and Upgrade systemhtac
showtext "Receiving and applying Ubuntu updates to the latest version..."
{
	eval "$_APTGET" update
	eval "$_APTGET" upgrade
	eval "$_APTGET" dist-upgrade
	eval "$_APTGET" autoremove -y
} 2>&1 | tee -a "$DEBUG_LOG"

##Auto remove any obsolete packages

##Clone Nodo to device from git
showtext "Cloning Nodo to device from git..."
# Update Link
cd || exit 1
git clone --single-branch https://github.com/MoneroNodo/Nodo.git
cd Nodo || exit 1
git reset --hard HEAD

##Replace file /etc/sudoers to set global sudo permissions/rules (required to add  new permissions to www-data user for interface buttons)
showtext "Downloading and replacing /etc/sudoers file..."
chmod 0440 home/nodo/sudoers
chown root home/nodo/sudoers
cp "${_cwd}"/home/nodo/sudoers /etc/sudoers

#ubuntu /dev/null odd requirment to set permissions
chmod 777 /dev/null
showtext "Global permissions changed"

#Backup User values
showtext "Creating backups of any settings you have customised"
#home dir
mv /home/nodo/variables/config.json /home/nodo/variables/config_retain.json
#variables dir
showtext "User configuration saved"
#Install Update

showtext "setup-nodo.sh..."
. "${_cwd}"/setup-nodo.sh

showtext "Merge config.json"
jq -s '.[0] * .[1] | {config: .config}' /home/nodo/variables/config_retain.json "${_cwd}"/home/nodo/variables/config.json > /home/nodo/variables/config.json || \
	cp -f /home/nodo/variables/config_retain.json /home/nodo/config.json

showtext "User configuration restored"

##Update crontab
showtext "Updating crontab tasks..."
crontab "${_cwd}"/var/spool/cron/crontabs/nodo 2> >(tee -a "$DEBUG_LOG" >&2)

#Update system version number to new one installed
{
	showtext "Updating system version number..."
	putvar "versions.nodo" "$RELEASE"
	#ubuntu /dev/null odd requiremnt to set permissions
	chmod 777 /dev/null
} 2>&1 | tee -a "$DEBUG_LOG"

##End debug log
showtext "
####################
End update-nodo.sh script $(date)
####################
"
