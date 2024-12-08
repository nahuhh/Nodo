#!/bin/bash -e
### BEGIN INIT INFO
# Provides:          friendlyelec
# Required-Start:
# Required-Stop:
# Default-Start:
# Default-Stop:
# Short-Description:
# Description:       Init Onboard LEDs
### END INIT INFO

PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

WAN=eth0
LAN1=eth1
LAN2=eth2

MODEL=$(tr -d '\0' < /proc/device-tree/board/model)
BOARD=Nodo-N6

if [ -d /sys/class/leds/wan_led ]; then
        echo netdev > /sys/class/leds/wan_led/trigger
        echo ${WAN} > /sys/class/leds/wan_led/device_name
        echo 1 > /sys/class/leds/wan_led/link
fi

if [ -d /sys/class/leds/lan_led ]; then
        echo netdev > /sys/class/leds/lan_led/trigger
        echo ${LAN1} > /sys/class/leds/lan_led/device_name
        echo 1 > /sys/class/leds/lan_led/link
else
        if [ -d /sys/class/leds/lan1_led ]; then
                echo netdev > /sys/class/leds/lan1_led/trigger
                echo ${LAN1} > /sys/class/leds/lan1_led/device_name
                echo 1 > /sys/class/leds/lan1_led/link
        fi

        if [ -d /sys/class/leds/lan2_led ]; then
                echo netdev > /sys/class/leds/lan2_led/trigger
                echo ${LAN2} > /sys/class/leds/lan2_led/device_name
                echo 1 > /sys/class/leds/lan2_led/link
        fi
fi
