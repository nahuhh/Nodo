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

if [ ! -f /etc/firstuse ]; then
    /usr/local/bin/gen-friendlyelec-release
    . /etc/friendlyelec-release
    /bin/echo ${BOARD} > /etc/hostname
    /bin/sed -i "s/\(127.0.1.1\s*\).*/\1${BOARD}/g" /etc/hosts
    /bin/hostname ${BOARD}

    case ${BOARD} in
    NanoPi-R5S*|NanoPi-R6S)
        remove_unnecessary_network_settings 3
        ;;
    SOM-4418|NanoPi-R1|NanoPi-R1S-H3|NanoPi-R1S-H5|NanoPi-R4S|NanoPi-R4SE|NanoPi-R2S*|NanoPi-R2C|NanoPi-R2C-Plus|Core3328|NanoPi-R5C|NanoPC-T6*|NanoPi-R6C)
        remove_unnecessary_network_settings 2
        ;;
    NanoPi-NEO-Air)
        rm -f /etc/network/interfaces.d/eth*
        ;;
    *)
        remove_unnecessary_network_settings 1
        ;;
    esac

    ldconfig || true
    /bin/echo "0" > /etc/firstuse
fi

