#!/bin/bash

#shellcheck source=home/nodo/common.sh
. /home/nodo/common.sh

CONF=$(</home/nodo/variables/config.json)
getvar() {
	echo "$CONF" | jq -r ".config.$1"
}

MONERO_PORT=$(getvar "monero_port")
MONERO_PUBLIC_PORT=$(getvar "monero_public_port")

RPC_ENABLED=$(getvar "rpc_enabled")
RPC_PORT=$(getvar "monero_rpc_port")
RPCu=$(getvar "rpcu")
RPCp=$(getvar "rpcp")

IN_PEERS=$(getvar "in_peers")
OUT_PEERS=$(getvar "out_peers")

LIMIT_RATE_UP=$(getvar "limit_rate_up")
LIMIT_RATE_DOWN=$(getvar "limit_rate_down")

DATA_DIR=$(getvar "data_dir")

TORPROXY_ENABLED=$(getvar "torproxy_enabled")

I2P_ENABLED=$(getvar "i2p_enabled")
I2P_PEER=$(getvar "add_i2p_peer")
I2P_PORT=$(getvar "i2p_port")
I2P_ADDRESS=$(getvar "i2p_address")

TOR_ENABLED=$(getvar "tor_enabled")
TOR_PEER=$(getvar "add_tor_peer")
TOR_PORT=$(getvar "tor_port")
TOR_ADDRESS=$(getvar "tor_address")

DATA_DIR=$(getvar "data_dir")
SYNC_MODE=$(getvar "sync_mode")

DEVICE_IP="0.0.0.0"

putvar "boot_status" "3"
#Start Monerod
if [ "$TORPROXY_ENABLED" != "TRUE" ]; then
	if [ "$I2P_ENABLED" == "TRUE" ]; then
		cln_flags="--proxy=127.0.0.1:4447 "
	else
		cln_flags="--proxy=127.0.0.1:9050 "
	fi
fi
if [ "$I2P_ENABLED" == "TRUE" ]; then
	i2p_args="--tx-proxy=\"i2p,127.0.0.1:4447,64\" ${I2P_ADDRESS:+--anonymous-inbound=$I2P_ADDRESS,127.0.0.1:$I2P_PORT} ${I2P_PEER:+--add-priority-node=$I2P_PEER} "
fi
if [ "$TOR_ENABLED" == "TRUE" ]; then
	tor_args="--tx-proxy=\"tor,127.0.0.1:9050,64\" ${TOR_ADDRESS:+--anonymous-inbound=$TOR_ADDRESS:$TOR_PORT,127.0.0.1:$TOR_PORT} ${TOR_PEER:+--add-priority-node=$TOR_PEER} "
fi
if [ "$RPC_ENABLED" == "TRUE" ]; then
	rpc_args="--rpc-restricted-bind-ip=\"$DEVICE_IP\" --rpc-restricted-bind-port=\"$RPC_PORT\" --rpc-login=\"$RPCu:$RPCp\" --rpc-ssl disabled "
fi
location=/home/nodo/monero/build/release/bin
eval "$location"/monerod "$i2p_args$tor_args$rpc_args$cln_flags" --db-sync-mode="$SYNC_MODE" --data-dir="$DATA_DIR" --zmq-pub "tcp://$DEVICE_IP:18083" --confirm-external-bind --in-peers="$IN_PEERS" --out-peers="$OUT_PEERS" --limit-rate-up="$LIMIT_RATE_UP" --limit-rate-down="$LIMIT_RATE_DOWN" --max-log-file-size=10485760 --log-level=0 --max-log-files=1 --enable-dns-blocklist --p2p-bind-port="$MONERO_PORT" --rpc-bind-port="$MONERO_PUBLIC_PORT" --non-interactive
