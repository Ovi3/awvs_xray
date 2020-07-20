#!/bin/bash
# Date：2020年3月31日
# Author: Ovi3

iptables -L INPUT | grep tcp | grep 3443 | grep DROP >> /dev/null 2>&1

if [ $? -ne 0 ] ;then
  echo "Close tcp:3443"
  iptables -A INPUT ! -i lo -p tcp --dport 3443 -j DROP
else
  echo "Open tcp:3443"
  iptables -D INPUT ! -i lo -p tcp --dport 3443 -j DROP
fi

