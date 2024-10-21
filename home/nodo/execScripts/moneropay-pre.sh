#!/bin/bash

# *** *generate\_from\_keys*
#
# Restores a wallet from a given wallet address, view key, and optional spend key.
#
# Inputs:
#
# - /restore\_height/  - integer; (Optional; defaults to 0) The block height to restore the wallet from.
# - /filename/  - string; The wallet's file name on the RPC server.
# - /address/  - string; The wallet's primary address.
# - /spendkey/  - string; (Optional; omit to create a view-only wallet) The wallet's private spend key.
# - /viewkey/  - string; The wallet's private view key.
# - /password/  - string; The wallet's password.
# - /autosave\_current/  - boolean; (Defaults to true) If true, save the current wallet before generating the new wallet.
#
# Outputs:
#
# - /address/  - string; The wallet's address.
# - /info/  - string; Verification message indicating that the wallet was generated successfully and whether or not it is a view-only wallet.
#shellcheck source=home/nodo/common.sh
. /home/nodo/common.sh

{
read -r ADDR
read -r VKEY
read -r PORT
} < <(
	jq -r '.config | .moneropay.address, .moneropay.viewkey, .monero_public_port' $CONFIG_FILE
)

HEIGHT="$(curl -ls http://127.0.0.1:"$PORT"/get_height -H 'Content-Type: application/json' | jq -r .height)"

if [ -f /home/nodo/mpay.keys ]; then
	printf %s '{"jsonrpc":"2.0","id":"0","method":"open_wallet","params":{"filename": "mpay", "password":"mpaypass"}}' | curl http://127.0.0.1:34512/json_rpc --json @-
else
printf %s '{"jsonrpc":"2.0","id":"0","method":"generate_from_keys", "params":{"restore_height": %s, "wallet_name": "mpay", "address": "%s", "viewkey": "%s", "filename": "mpay", "password": "mpaypass"}}' "$HEIGHT" "$ADDR" "$VKEY" | curl http://127.0.0.1:34512/json_rpc --json @-
fi

printf '{"jsonrpc":"2.0","id":"0","method":"set_daemon","params": {"address":"http://localhost:%s","trusted":true}}' "$PORT" | curl localhost:34512/json_rpc --json @- &
