#!/bin/bash
# Date：2020年3月31日
# Author: Ovi3

if [[ $# -lt 2 ]]; then
  echo -ne "Usage: $0 yourip xray_count\n"
  exit
fi

# start awvs
service docker start
# docker pull vouu/acunetix and run
docker run -it -d --network host --name awvs13 vouu/acunetix
# only localhost can access awvs
iptables -L INPUT | grep tcp | grep 3443 | grep DROP >> /dev/null 2>&1
if [ $? -ne 0 ] ;then
  iptables -A INPUT ! -i lo -p tcp --dport 3443 -j DROP
fi

mkdir ./output >> /dev/null 2>&1

# generate xray config_tmpl.yaml、reverse.yaml
rm ./core/config.yaml >> /dev/null 2>&1
./core/xray_linux_amd64 version
python3 ./core/modify.py

# start xray
./core/start_xray.sh $1 $2
