#!/bin/bash

#shellcheck source=home/nodo/common.sh
. /home/nodo/common.sh

lwsloc=/home/nodo/monero-lws/build/src/

DATA_DIR=$(getvar "data_dir")/light_wallet_server
PORT=8135

eval "${lwsloc}monero-lws-daemon --daemon tcp://127.0.0.1:18082 --db-path $DATA_DIR --admin-rest-server http://127.0.0.1:${PORT}/admin --rest-server http://127.0.0.1:${PORT}/basic"
