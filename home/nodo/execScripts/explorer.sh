#!/bin/bash

#shellcheck source=home/nodo/common.sh
. /home/nodo/common.sh

exploc=/home/nodo/onion-monero-blockchain-explorer/build/
DATA_DIR=$(getvar "data_dir")/lmdb
MONERO_RPC_PORT=$(getvar "monero_rpc_port")
MONEROD="127.0.0.1:$MONERO_RPC_PORT}"
RPC_ENABLED=$(getvar "rpc_enabled")
if [ "$RPC_ENABLED" == "TRUE" ]; then
	RPCp=$(getvar "rpcp")
	RPCu=$(getvar "rpcu")
fi

eval "$exploc/xmrblocks -d $MONEROD ${RPCp:+--daemon-login $RPCp:$RPCu} --enable-json-api=1 -b $DATA_DIR"
