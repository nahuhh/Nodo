#!/bin/sh
xrandr -o left
xinput set-float-prop "pointer:goodix-ts" 175 0.000000 -1.000000 1.000000 1.000000 0.000000 0.000000 0.000000 0.000000 1.000000
xsetroot -bitmap mp.xbm
[ -f /opt/nodo/embeddedUI.sh ] && exec EmbeddedUI/NodoUI
