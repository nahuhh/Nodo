#!/bin/bash

#shellcheck source=home/nodo/common.sh
. /home/nodo/common.sh

WALLET_ADDRESS=$(getvar "mining.address")

eval /home/nodo/p2pool/build/p2pool --mini --host 127.0.0.1 --wallet "$WALLET_ADDRESS"
