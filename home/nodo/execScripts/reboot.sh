#!/bin/bash
sudo systemctl stop block-explorer.service
sudo systemctl stop log-io-file.service
sudo systemctl stop log-io-server.service
sudo systemctl stop monero-lws.service
sudo systemctl stop monero-lws-admin.service
sudo systemctl stop moneroI2PPrivate.service
sudo systemctl stop moneroPrivate.service
sudo systemctl stop moneroPublicFree.service
sudo systemctl stop moneroPublicRPCPay.service
sudo systemctl stop moneroTorPrivate.service
sudo systemctl stop moneroTorPublic.service
sudo systemctl stop noip.service
#Shutdown
sleep 10
sudo reboot
