#!/bin/bash

#shellcheck source=home/nodo/common.sh
. /home/nodo/common.sh

{
read -r DATA_DIR
read -r MONERO_RPC_PORT
read -r RPC_ENABLED
if [ "$RPC_ENABLED" == "TRUE" ]; then
	read -r RPCu
	read -r RPCp
fi
} < <(
jq -r '.config | .data_dir, .monero_rpc_port, .rpc_enabled, .rpcu, .rpcp' < $CONFIG_FILE
)

MONEROD="127.0.0.1:$MONERO_RPC_PORT}"

eval "/home/nodo/bin/xmrblocks --daemon-url=$MONEROD ${RPCp:+--daemon-login $RPCu:$RPCp} --enable-json-api=1 -b $DATA_DIR/lmdb"
