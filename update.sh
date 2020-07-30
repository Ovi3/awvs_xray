#!/bin/bash
# Date：2020年3月31日
# Author: Ovi3

# update xray
rm ./core/xray_linux_amd64 >> /dev/null 2>&1
wget https://github.com/chaitin/xray/releases/latest/download/xray_linux_amd64.zip && unzip xray_linux_amd64.zip -d ./core/ && rm xray_linux_amd64.zip
