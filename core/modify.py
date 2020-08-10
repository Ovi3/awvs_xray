#!/usr/bin/python3
# -*-coding:utf-8-*-

"""
Date：2020年3月31日
Author: Ovi3

修改reverse_tmpl.yaml，填充token值，生成reverse.yaml
修改config.yaml生成config_tmpl.yaml
"""


import os
import re
import random
import string

base_dir = os.path.dirname(os.path.realpath(__file__))
reverse_path = os.path.join(base_dir, "./reverse.yaml")
reverse_tmpl_path = os.path.join(base_dir, "./reverse_tmpl.yaml")
config_path = os.path.join(base_dir, "./config.yaml")
config_tmpl_path = os.path.join(base_dir, "./config_tmpl.yaml")

token = "".join([random.choice(string.ascii_letters + string.digits) for i in range(0, 8)])
reverse = open(reverse_tmpl_path, "r", encoding="utf-8").read()
reverse = reverse.replace("{{TOKEN}}", token)
open(reverse_path, "w", encoding="utf-8").write(reverse)

config = open(config_path, "r", encoding="utf-8").read()
config = config.replace("detect_cors_header_config: true", "detect_cors_header_config: false")\
    .replace("detect_blind_injection: false", "detect_blind_injection: true")\
    .replace("detect_none_injection_case: false", "detect_none_injection_case: true")\
    .replace("dirscan:\n    enabled: true", "dirscan:\n    enabled: false")\
    .replace("brute_force:\n    enabled: true", "brute_force:\n    enabled: false")\
    .replace("level: info", "level: warn")\
    .replace("token: \"\"", "token: \"%s\"" % token)\
    .replace("http:\n    enabled: true", "http:\n    enabled: false")\
    .replace("http_base_url: \"\"", "http_base_url: \"http://{{IP}}:7381\"")\
    .replace("dns_server_ip: \"\"", "dns_server_ip: \"{{IP}}\"")\
    .replace("remote_server: false", "remote_server: true")

config = re.sub(r"max_length: \d+", "max_length: 6000", config)

open(config_tmpl_path, "w", encoding="utf-8").write(config)
