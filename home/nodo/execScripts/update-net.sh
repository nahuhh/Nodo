#!/bin/bash

CONF=$(</home/nodo/variables/config.json)

WIFI_CONNAME="nodo-wireless"
ETH_CONNAME="nodo-ethernet"

read WIFI_ENABLED WIFI_SSID WIFI_PW WIFI_AUTO \
	WIFI_IP WIFI_SUBNET WIFI_ROUTER WIFI_DHCP < <(
echo "$CONF" | jq -r '.config.wifi | .enabled, .ssid, .pw, .auto, .ip, .subnet, .router, .dhcp'
)

read ETH_ENABLED ETH_AUTO ETH_IP ETH_SUBNET \
	ETH_ROUTER ETH_DHCP < <(
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
