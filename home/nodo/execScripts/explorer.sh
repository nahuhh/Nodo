#!/bin/bash

#shellcheck source=home/nodo/common.sh
. /home/nodo/common.sh

exploc=/home/nodo/onion-monero-blockchain-explorer/build/
DATA_DIR=$(getvar "data_dir")
MONEROD="127.0.0.1:"$(getvar "monero_public_port")

eval "$exploc/xmrblocks -d $MONEROD --enable-json-api=1 -b $DATA_DIR" >/dev/null
