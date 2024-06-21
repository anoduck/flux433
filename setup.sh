#!/usr/bin/env bash

WORKDIR="/opt/flux433"
CONF="/etc/flux433/config.ini"

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

if [[ ! -d $WORKDIR ]]; then
    mkdir -p $WORKDIR
fi

adduser --system --no-create-home --disabled-login --disabled-password --group flux433
usermod -aG plugdev flux433
mkdir -p /var/run/flux433 && chown -R flux433:flux433 /var/run/flux433 && chmod -R 775 /var/run/flux433 && chown -R flux433:flux433 $WORKDIR
git clone https://github.com/anoduck/flux433 "$WORKDIR"

if [[ ! -f $CONF ]]; then
    sudo -u flux433 "/usr/bin/python3" "$WORKDIR/flux433/start.py" --config "$CONF"
fi
cp "$WORKDIR/flux433.service" /etc/systemd/system/

systemctl daemon-reload