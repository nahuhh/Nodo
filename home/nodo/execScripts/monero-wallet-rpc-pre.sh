#!/bin/bash

if [ ! -d /opt/moneropay ]; then
	adduser --system --group moneropay
	mkdir -p /opt/moneropay
	chown -R moneropay:moneropay /opt/moneropay
	chmod -R 600
fi

