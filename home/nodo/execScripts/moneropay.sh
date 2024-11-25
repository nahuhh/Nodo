#!/bin/bash

#shellcheck source=home/nodo/common.sh
. /home/nodo/common.sh


/home/nodo/bin/moneropay -zero-conf=true -rpc-address="http://127.0.0.1:34512/json_rpc" -sqlite="file:///home/nodo/moneropay.sqlite" -bind="127.0.0.1:5000"
