#!/bin/bash -e
### BEGIN INIT INFO
# Provides:          friendlyelec
# Required-Start:
# Required-Stop:
# Default-Start:
# Default-Stop:
# Short-Description:
# Description:       Init board
### END INIT INFO

PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

BOARD=Nodo-N6

remove_unnecessary_network_settings() {
    for f in $(ls /etc/network/interfaces.d); do
        found=0
        for ((i=0;i<${1};i++)); do
            if [ "$f" = "eth${i}" ]; then
                found=1
            fi
        done
        if [ $found -eq 0 ]; then
            rm -f /etc/network/interfaces.d/$f
        fi
    done
}

remove_unnecessary_network_settings 2
ldconfig || true
/bin/echo "0" > /etc/firstuse
