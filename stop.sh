#!/bin/bash
# Date：2020年3月31日
# Author: Ovi3

cd "$(dirname $0)"
project_base=$(pwd)
awvs_path="${project_base}/core/awvs13.py"
output_dir="${project_base}/output"

echo "Notice: This will remove docker container include awvs scan task."
read -p "Press enter to continue"
# check if awvs has result and download report
python3 $awvs_path save https://127.0.0.1:3443/ ${output_dir}
docker rm -f awvs13 > /dev/null

tmux kill-session -t scan
tmux kill-session -t check

iptables -L INPUT | grep tcp | grep 3443 | grep DROP >> /dev/null 2>&1
if [ $? -eq 0 ] ;then
  echo "Open tcp:3443"
  iptables -D INPUT ! -i lo -p tcp --dport 3443 -j DROP
fi