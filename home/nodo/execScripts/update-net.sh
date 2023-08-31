#!/bin/bash

CONF=$(</home/nodo/variables/config.json)

WIFI_CONNAME="nodo-wireless"
ETH_CONNAME="nodo-ethernet"

{
read -r WIFI_ENABLED
read -r WIFI_SSID
read -r WIFI_PW
read -r WIFI_AUTO
read -r WIFI_IP
read -r WIFI_SUBNET
read -r WIFI_ROUTER
read -r WIFI_DHCP
} < <(
echo "$CONF" | jq -r '.config.wifi | .enabled, .ssid, .pw, .auto, .ip, .subnet, .router, .dhcp'
)

{
read -r ETH_ENABLED
read -r ETH_AUTO
read -r ETH_IP
read -r ETH_SUBNET
read -r ETH_ROUTER
read -r ETH_DHCP
} < <(
echo "$CONF" | jq -r '.config.ethernet | .enabled, .auto, .ip, .subjet, .router, .dhcp'
)

if [ "$ETH_ENABLED" = "TRUE" ]; then
	nmcli con show "$ETH_CONNAME" || \
		nmcli connection add type ethernet con-name "$ETH_CONNAME"

	if [ ! "$ETH_AUTO" = "TRUE" ]; then
		nmcli con modify "$ETH_CONNAME" ip4.method manual ip4.routes "$ETH_SUBNET" ip4.gateway "$ETH_ROUTER" ip4.address "$ETH_IP" ip4.dhcp-hostname "$ETH_DHCP"
	fi
	#<++> turn on ethernet
else
	true
	#<++> turn off ethernet (not a good idea I think, it's just a plug)
fi

if [ "$WIFI_ENABLED" = "TRUE" ]; then
	nmcli con show "$WIFI_CONNAME" || \
		nmcli connection add type wifi con-name "$WIFI_CONNAME"

	nmcli con modify "$WIFI_CONNAME" ssid "$WIFI_SSID" wifi-sec.psk "$WIFI_PW"

	if [ ! "$WIFI_AUTO" = "TRUE" ]; then
		nmcli con modify "$WIFI_CONNAME" ip4.method manual ip4.routes "$WIFI_SUBNET" ip4.gateway "$WIFI_ROUTER" ip4.address "$WIFI_IP" ip4.dhcp-hostname "$WIFI_DHCP"
	fi
	nmcli radio wifi on

else
	nmcli radio wifi off
fi
