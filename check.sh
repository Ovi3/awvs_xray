#!/bin/bash
# Date：2020年3月31日
# Author: Ovi3

cd "$(dirname $0)"
project_base=$(pwd)
xray_path="${project_base}/core/xray_linux_amd64"
awvs_path="${project_base}/core/awvs13.py"
urls_path="${project_base}/urls.txt"
scan_workspace="${project_base}/workspace"
output_dir="${project_base}/output"


# restart awvs every day
awvs_time="${scan_workspace}/awvs_time"
if [[ -f "$awvs_time" ]]; then
  latest=`cat "$awvs_time"`
  now=`date +%s`
  declare -i gap=$now-$latest
  if [[ $gap -ge 86400 ]]; then  # 60 * 60 * 24 sec = 1 day
    echo "Wait for awvs scan complete, and restart awvs"
    scanning=`python3 $awvs_path status https://127.0.0.1:3443/`
    if [[ $? -eq 0 && $scanning < 1 ]]; then
      python3 $awvs_path save https://127.0.0.1:3443/ ${output_dir}
      echo "restart awvs now"
      docker rm -f awvs13 > /dev/null
      sleep 1
      docker run -it -d --network host --name awvs13 vouu/acunetix

      echo `date +%s` > "$awvs_time"
    fi
    exit 0
  fi
else
  echo `date +%s` > "$awvs_time"
fi


# check if awvs has result and download report
python3 $awvs_path save https://127.0.0.1:3443/ ${output_dir}

session_name="scan"
tmux list-windows -t $session_name -F "#I #W" | while read line; do
  index=`echo $line | awk -F " " '{print $1}'`
  # sed '/./,$!d'       remove leading newline
  buffer=`tmux capture-pane -t $session_name:$index -p | tail -n 20 | tac | sed '/./,$!d'`
  lastline=$(echo "$buffer" | head -n 1)  # Cause the buffer had been "tac", the "head -n 1" is last line

  if [ "$index" = "0" ]; then
    # check xray reverse is crash. The xray reverse doesn't crash possibly unless memory is exhausted
    fmt='\u@\h:'
    if [[ "$lastline" =~ "${fmt@P}" ]]; then
      echo "xray reverse is crash, start it"
      tmux send-keys -t $session_name:$index "$xray_path --config ./reverse.yaml reverse " C-m
    fi
    continue
  fi

  port=`echo $line | awk -F ' ' '{print $2}'`

  # check xray if crash
  fmt='\u@\h:'
  if [[ "$lastline" =~ "${fmt@P}" ]]; then
    # xray is crash
    echo "xray(${port}) is crash, start it"
    tmux send-keys -t $session_name:$port "$xray_path --config ./config.yaml webscan --listen 127.0.0.1:$port --html-output ${output_dir}/result_$(date '+%Y%m%d%H%M')_${port}.html" C-m
    # 这里只启动xray，在下次该脚本检查到xray刚启动的时候再添加awvs扫描任务
    # python3 $awvs_path add https://127.0.0.1:3443/ ${urls_path} ${output_dir} 127.0.0.1 $port
    continue
  fi

  # print status
  pending0=0
  hasprint=0
  while read -r bline; do
    if [[ $bline =~ "pending: 0" ]]; then
      pending0=`expr $pending0 + 1`
    fi
    if [[ $bline =~ ^Statistic\:.* ]]; then
      if [[ $hasprint -eq 0 ]]; then
        echo "xray(${port}) status: ${bline}"
        hasprint=1
      fi
    fi
  done <<< "$buffer"

  # 判断1分钟后扫描状态是否还是pending: 0，是则视为扫描完成
  status="${scan_workspace}/status_${index}"
  while read -r bline; do
    if [[ "$bline" =~ "pending:" ]]; then
      if [[ "$bline" =~ "pending: 0" ]]; then
        if [[ -f "$status" ]]; then
          latest=`cat "$status"`
          now=`date +%s`
          declare -i gap=$now-$latest
          if [[ $gap -ge 60 ]]; then
            pending0=2  # 标记为扫描完成
            break
          fi
        else
          echo `date +%s` > "$status"  # 不存在status文件才记录此时pending的时间戳
        fi
      else
        rm "$status" >> /dev/null 2>&1  # 状态不是pending0则删除status文件
      fi

      break
    fi
  done <<< "$buffer"


  # 判断xray是否扫描完成
  if [[ "$pending0" -ge 2 ]]; then
    rm "$status" >> /dev/null 2>&1  # 要重启xray了，所以删除status文件
    echo "xray(${port}) is done, restart it"
    tmux send-keys -t $session_name:$port C-c
    # wait xray shutdown
    sleep 5
    tmux send-keys -t $session_name:$port "$xray_path --config ./config.yaml webscan --listen 127.0.0.1:$port --html-output ${output_dir}/result_$(date '+%Y%m%d%H%M')_${port}.html" C-m
    sleep 3
    python3 $awvs_path add https://127.0.0.1:3443/ ${urls_path} ${output_dir} 127.0.0.1 $port
    continue
  fi

  # check xray if just start
  if [[ ! ${buffer} =~ "Statistic:" && (${buffer} =~ "starting mitm server" || ${buffer} =~ "Enabled plugins") ]]; then
    # xray is crash
    echo "xray(${port}) just start"
    python3 $awvs_path add https://127.0.0.1:3443/ ${urls_path} ${output_dir} 127.0.0.1 $port
    continue
  fi
done
