#!/bin/bash

#shellcheck source=home/nodo/common.sh
. /home/nodo/common.sh

{
read -r MONERO_PUBLIC_PORT
read -r ADDRESS
} < <(
        jq '.config | .monero_public_port, .mining.address' $CONFIG_FILE
)
eval /home/nodo/bin/xmrig -o 127.0.0.1:"$MONERO_PUBLIC_PORT" --randomx-1gb-pages -a rx/0 -u "$ADDRESS" --daemon
