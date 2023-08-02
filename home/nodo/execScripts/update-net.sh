#!/bin/bash

CONF=$(</home/nodo/variables/config.json)
getvar() {
	echo "$CONF" | jq -r ".config.$1"
}

WIFI_CONNAME="nodo-wireless"
ETH_CONNAME="nodo-ethernet"

WIFI_ENABLED=$(getvar "wifi.enabled")
WIFI_SSID=$(getvar "wifi.ssid")
WIFI_PW=$(getvar "wifi.pw")
WIFI_AUTO=$(getvar "wifi.auto")
WIFI_IP=$(getvar "wifi.ip")
WIFI_SUBNET=$(getvar "wifi.subnet")
WIFI_ROUTER=$(getvar "wifi.router")
WIFI_DHCP=$(getvar "wifi.dhcp")

ETH_ENABLED=$(getvar "ethernet.enabled")
ETH_AUTO=$(getvar "ethernet.auto")
ETH_IP=$(getvar "ethernet.ip")
ETH_SUBNET=$(getvar "ethernet.subnet")
ETH_ROUTER=$(getvar "ethernet.router")
ETH_DHCP=$(getvar "ethernet.dhcp")

if [ "$ETH_ENABLED" = "TRUE" ]; then
	true
	nmcli con show "$ETH_CONNAME" || \ #create connection if not existing
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
	nmcli con show "$WIFI_CONNAME" || \ #create connection if not existing
		nmcli connection add type wifi con-name "$WIFI_CONNAME"

	nmcli con modify "$WIFI_CONNAME" ssid "$WIFI_SSID" wifi-sec.psk "$WIFI_PW"

	if [ ! "$WIFI_AUTO" = "TRUE" ]; then
		nmcli con modify "$WIFI_CONNAME" ip4.method manual ip4.routes "$WIFI_SUBNET" ip4.gateway "$WIFI_ROUTER" ip4.address "$WIFI_IP" ip4.dhcp-hostname "$WIFI_DHCP"
	fi
	nmcli radio wifi on

else
	nmcli radio wifi off
fi
