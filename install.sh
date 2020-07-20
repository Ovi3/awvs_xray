#!/bin/bash
# Date：2020年3月31日
# Author: Ovi3
set -x

apt update
apt install -y unzip python3 python3-pip tmux wget
python3 -m pip install -r requirements.txt

# download latest xray, see: https://help.github.com/en/github/administering-a-repository/linking-to-releases
wget https://github.com/chaitin/xray/releases/latest/download/xray_linux_amd64.zip && unzip xray_linux_amd64.zip -d ./core/ && rm xray_linux_amd64.zip

# httprobe
wget https://github.com/tomnomnom/httprobe/releases/download/v0.1.2/httprobe-linux-amd64-0.1.2.tgz && tar -zxvf httprobe-linux-amd64-0.1.2.tgz -C ./core/ && rm httprobe-linux-amd64-0.1.2.tgz

# 关掉udp53端口占用
systemctl stop systemd-resolved
rm /etc/resolv.conf
echo "nameserver 8.8.8.8" > /etc/resolv.conf

# docker
service docker status >> /dev/null 2>&1
if [ $? -ne 0 ] ;then
  curl -s https://get.docker.com/ | sh
fi

