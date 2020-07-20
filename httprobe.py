#!/usr/bin/python3
# -*-coding:utf-8-*-

"""
Date：2020年3月31日
Author: Ovi3
"""

import os
import sys
import subprocess
import shlex

HTTPPROBE_BIN_PATH = "./core/httprobe"


def httprobe(domains_path, output_path=None):
    """
    通过调用httprobe获取域名是否开启http/https服务，若http和https都开启则只存储https
    httprobe不支持指定代理， httprobe不获取网站标题
    :param domains_path: 包含域名列表的txt文件
    """
    domains_path = os.path.abspath(domains_path)
    if output_path:
        if not os.path.isdir(os.path.dirname(os.path.abspath(output_path))):
            print("Can't write to " + os.path.abspath(output_path))
            return
    else:
        output_path = domains_path[:domains_path.rindex(".")] + "_httprobe.txt"

    domains = []
    with open(domains_path, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                domains.append(line)

    cmd = HTTPPROBE_BIN_PATH.replace("\\", "/")
    cmd = shlex.split(cmd)
    print("Wait for httprobe to finish...")
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    stdoutdata, stderrdata = p.communicate("\n".join(domains).encode())
    stdoutdata = stdoutdata.decode()

    result = {}
    for d in domains:
        result.update({d: []})

    for line in stdoutdata.split("\n"):
        if line.startswith("http://"):
            domain = line[len("http://"):]
            result.get(domain).append("HTTP")
        if line.startswith("https://"):
            domain = line[len("https://"):]
            result.get(domain).append("HTTPS")

    with open(output_path, "a") as f_out:
        for domain, protos in result.items():
            if "HTTPS" in protos:
                f_out.write("https://" + domain + "\n")
            elif "HTTP" in protos:
                f_out.write("http://" + domain + "\n")

    print("Save in %s" % os.path.abspath(output_path))


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: %s <domains_path> <output_path> [httprobe_path]" % sys.argv[0])
        exit(1)
    if len(sys.argv) > 3:
        HTTPPROBE_BIN_PATH = os.path.abspath(sys.argv[3])
    httprobe(sys.argv[1], sys.argv[2])
