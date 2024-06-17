#!/usr/bin/env bash

WORKDIR="/opt/flux433"

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

if [[ ! -d $WORKDIR ]]; then
    mkdir -p $WORKDIR
fi

deluser flux433
delgroup flux433
rm -rf "$WORKDIR"
rm -rf /var/run/flux433
rm -rf /var/log/flux433
rm -rf /etc/systemd/system/flux433.service
systemctl daemon-reload