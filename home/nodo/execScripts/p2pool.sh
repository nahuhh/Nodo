#!/bin/bash

#shellcheck source=home/nodo/common.sh
. /home/nodo/common.sh

WALLET_ADDRESS=$(getvar "mining.address")
{
	read -r WALLET_ADDRESS
	read -r RPC_ENABLED
	read -r RPCP
	read -r RPCU
	read -r RPC_PORT
} < <(
jq -r '.config | .mining.address, .rpc_enabled, .rpcp, .rpcu, .monero_public_port' $CONFIG_FILE
)

if [ -n "$RPC_ENABLED" ]; then
	eval /home/nodo/p2pool/build/p2pool --mini --host 127.0.0.1 --rpc-port "$RPC_PORT" --wallet "$WALLET_ADDRESS" --rpc-login "$RPCU:$RPCP"
else
	eval /home/nodo/p2pool/build/p2pool --mini --host 127.0.0.1 --rpc-port "$RPC_PORT" --wallet "$WALLET_ADDRESS"
fi
