#!/bin/bash

. /home/nodo/common.sh

{
read -r ADDR
} < <(
	jq -r '.config | .moneropay.deposit_address' $CONFIG_FILE
)

if [ -z "$ADDR" ] || [ "null" = "$ADDR" ]; then
	exit 0
fi

printf '{"jsonrpc":"2.0","id":"0","method":"sweep_all","params":{"address": "%s", "subaddr_indices_all": true}}' "$ADDR" | curl http://127.0.0.1:34512/json_rpc --json @-
