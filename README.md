### 简介
在Ubuntu18.08 x64下搭建AWVS13和xray的自动化扫描。

xray：https://github.com/chaitin/xray/releases

awvs13：https://hub.docker.com/r/vouu/acunetix

awvs13的邮箱、密码：contact@manhtuong.net、Abcd1234

### 功能
- 下载安装xray、awvs docker镜像
- xray多开，开启xray回连平台
- 监听xray是否扫描完成，如果是就扫描下一个url

高度定制化功能：
- awvs仅作爬取，不扫描，扫描由xray进行
- 使用iptables设置AWVS监听的3443端口仅本地访问
- 定时下载awvs报告并删除awvs容器里的报告
- 每24小时重启AWVS，以释放内存（AWVS容器运行久了，内存越占越满）
- xray配置：关闭目录爆破、密码爆破

（本仓库代码功能高度定制，每个人的需求不一样。本仓库代码仅供参考）


### 文件说明

- install.sh：下载xray、httprobe，安装docker，awvs
- toggle.sh： 开关TCP:3443端口对外开放。因为AWVS账号密码固定，需要其它机器访问该端口时再开放
- start.sh： 开始运行xray和awvs
- check.sh：检测xray运行状态，如果扫描完成则调用awvs添加扫描任务
- update.sh： 升级xray
- core/awvs13.py： 用于添加awvs扫描任务等
- core/start_xray.sh： xray被动扫描多开脚本
- core/reverse_tmpl.yaml：xray回连平台配置文件模板
- core/modify.py：修改xray配置文件config.yaml，生成config_tmpl.yaml

以下为运行时生成的文件：
- core/config_tmpl.yaml：xray扫描配置文件模板
- core/reverse.yaml：xray回连平台配置文件
- output/result_*.html： xray扫描报告
- output/*.pdf： awvs扫描报告
- output/urls_done.txt： 已添加过awvs扫描任务的url列表
- workspace/： xray的临时工作目录

### 运行步骤
在一台外网服务器，Ubuntu18.08上运行：

```shell script
chmod +x *.sh core/*.sh
# 安装
./install.sh

# 将url列表文件放在项目根目录的urls.txt文件，供awvs13读取
# 可以使用httprobe验证domains.txt域名列表文件里的域名是否开web服务，生成urls.txt文件
python3 httprobe.py domains.txt urls.txt

# 运行awvs13容器；通过tmux开启多个xray；通过tmux每60秒运行一次./check.sh，用于监控xray扫描状态
./start.sh <外网IP> <xray个数>

# 关闭xray、awvs13容器
# 注意该脚本会删除awvs13容器，确保awvs13里无扫描任务再执行
./stop.sh

# 通过tmux进入会话查看xray扫描状态或check.sh脚本运行状态
tmux a -t scan
tmux a -t check
```



