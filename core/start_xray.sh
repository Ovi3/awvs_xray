#!/bin/bash
# Date：2020年3月31日
# Author: Ovi3

# need these files in current dir: xray_linux_amd64, config_tmpl.yaml, reverse.yaml
# incovked by run.sh

project_base=$(pwd)
xray_path="${project_base}/core/xray_linux_amd64"
config_tmpl_path="${project_base}/core/config_tmpl.yaml"
reverse_path="${project_base}/core/reverse.yaml"
scan_workspace="${project_base}/workspace"
output_dir="${project_base}/output"

if [[ $# -lt 1 ]]; then
  echo -ne "Usage: $0 yourip [xray_count] \n\txray_count is 3 by default.\n"
  exit
fi
yourip=$1

xray_count=3
if [[ $# -ge 2 ]]; then
  xray_count=$2
fi

if [ ! -f $config_tmpl_path ]; then
  echo "$config_tmpl_path not exist"
  exit
fi

if [ -d $scan_workspace ]; then
  rm $scan_workspace -rf
fi
mkdir $scan_workspace


sed  -e "s/{{IP}}/$yourip/g" $config_tmpl_path > "${scan_workspace}/config.yaml"
cp ${reverse_path} "${scan_workspace}/reverse.yaml"


session_name="scan"
start_port=7621
ports=$(seq $start_port "$(expr $start_port + $xray_count - 1)")
echo -n "$ports" | tr '\n' ',' | xargs -i echo "ports: {}"

# start xray
tmux has-session -t $session_name >/dev/null 2>&1
if [ $? != 0 ]; then
  {
    reverse_window="reverse"
    tmux new-session -s $session_name -n $reverse_window -d
    tmux send-keys -t $session_name:$reverse_window "cd $scan_workspace" C-m
    tmux send-keys -t $session_name:$reverse_window "$xray_path --config ./reverse.yaml reverse " C-m
    # wait xary reverse server up
    sleep 3s

    for port in $ports; do
      {
        tmux new-window -t $session_name -n $port
        tmux send-keys -t $session_name:$port "cd $scan_workspace" C-m

        tmux send-keys -t $session_name:$port "$xray_path --config ./config.yaml webscan --listen 127.0.0.1:$port --html-output ${output_dir}/result_$(date '+%Y%m%d%H%M')_${port}.html" C-m
      }
    done
  }
else
  echo -ne "tmux session $session_name is exist, run tmux kill-session -t $session_name first\n"
fi

echo "xray is starting, wait for several seconds"
sleep 8

# add awvs crawl task every 60 seconds
session_name="check"
tmux has-session -t $session_name >/dev/null 2>&1
if [ $? != 0 ]; then
  tmux new-session -s $session_name -d
  tmux send-keys -t $session_name "cd $scan_workspace" C-m
  tmux send-keys -t $session_name "watch -n 60 ${project_base}/check.sh" C-m
else
  echo -ne "tmux session $session_name is exist, run tmux kill-session -t $session_name first\n"
fi
