#!/bin/sh

set -xe

echo 'APT::Periodic::Update-Package-Lists \"0\";' | tee    /etc/apt/apt.conf.d/51disable-unattended-upgrades
echo 'APT::Periodic::Unattended-Upgrade   \"0\";' | tee -a /etc/apt/apt.conf.d/51disable-unattended-upgrades

systemctl stop apt-daily.timer
systemctl disable apt-daily.timer
systemctl disable apt-daily.service
systemctl daemon-reload
