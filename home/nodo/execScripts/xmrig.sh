#!/bin/bash

#shellcheck source=home/nodo/common.sh
. /home/nodo/common.sh

eval /home/nodo/xmrig/build/xmrig -o 127.0.0.1:3333 -c /home/nodo/xmrig.json
