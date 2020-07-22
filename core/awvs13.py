#!/usr/bin/python3
# -*-coding:utf-8-*-

"""
Date：2020年3月31日
Author: Ovi3

批量添加AWVS13扫描任务
参考：https://github.com/ody5sey/Voyager/blob/master/app/lib/core/awvs_core.py
"""

import os
import sys
import time
import json
import hashlib
from urllib.parse import urlparse

import requests
requests.packages.urllib3.disable_warnings()


AWVS_USERNAME = "contact@manhtuong.net"
AWVS_PASSWORD = "Abcd1234"


class AWVS:
    def __init__(self, host_address):
        self.awvs_host_address = host_address

        self.awvs_x_auth = None
        self.awvs_header = None
        self.awvs_cookies = None

        self.target_id_list = []
        self.id_map_list = []

    def login(self):
        password = hashlib.sha256(AWVS_PASSWORD.encode()).hexdigest()
        data = {"email": AWVS_USERNAME, "password": password, "remember_me": False, "logout_previous": True}
        try:
            response = requests.post(self.awvs_host_address + "/api/v1/me/login", data=json.dumps(data),
                                     headers={"content-type": "application/json"},
                                     timeout=30,
                                     verify=False)

            self.awvs_x_auth = response.headers['X-Auth']
            self.awvs_header = {"X-Auth": self.awvs_x_auth, "content-type": "application/json"}
            self.awvs_cookies = {"ui_session":self.awvs_x_auth}

            return True
        except Exception as e:
            print("[-] Error:", str(e))
            return False

    def add_task(self, target):
        """
        向添加任务的函数
        :param target: http://127.0.0.1
        :return:e723c824-724c-4ae5-b0e0-1679c3d6aacf
        """
        data = {"address": target, "description": target, "criticality": "10"}
        try:
            response = requests.post(self.awvs_host_address + "/api/v1/targets", data=json.dumps(data),
                                     headers=self.awvs_header,
                                     cookies=self.awvs_cookies,
                                     timeout=30,
                                     verify=False)
            result = json.loads(response.content)

            self.target_id_list.append(result['target_id'])

            return result['target_id']
        except Exception as e:
            print("[-] Error:", str(e))
            return

    def start_task(self, url, cookie=None, proxy=None):
        # 添加target并开始扫描
        '''
        11111111-1111-1111-1111-111111111112    High Risk Vulnerabilities
        11111111-1111-1111-1111-111111111115    Weak Passwords
        11111111-1111-1111-1111-111111111117    Crawl Only
        11111111-1111-1111-1111-111111111116    Cross-site Scripting Vulnerabilities
        11111111-1111-1111-1111-111111111113    SQL Injection Vulnerabilities
        11111111-1111-1111-1111-111111111118    quick_profile_2 0   {"wvs": {"profile": "continuous_quick"}}
        11111111-1111-1111-1111-111111111114    quick_profile_1 0   {"wvs": {"profile": "continuous_full"}}
        11111111-1111-1111-1111-111111111111    Full Scan   1   {"wvs": {"profile": "Default"}}
        '''

        # 扫描设置
        data = {
            "excluded_paths": ["^.*logout.*$"],
            "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
            # "custom_headers": ["Accept: */*", "Referer:" + url, "Connection: Keep-alive"],
            # "custom_cookies": [{"url": url,
            #                     "cookie": "UM_distinctid=15da1bb9287f05-022f43184eb5d5-30667808-fa000-15da1bb9288ba9; PHPSESSID=dj9vq5fso96hpbgkdd7ok9gc83"}],
            # "scan_speed": "moderate",  # sequential/slow/moderate/fast more and more fast
            # "technologies": ["PHP"],  # ASP,ASP.NET,PHP,Perl,Java/J2EE,ColdFusion/Jrun,Python,Rails,FrontPage,Node.js
            # # 代理
            # "proxy": {
            #     "enabled": False,
            #     "address": "127.0.0.1",
            #     "protocol": "http",
            #     "port": 8080,
            #     "username": "aaa",
            #     "password": "bbb"
            # },
            # # 无验证码登录
            # "login": {
            #     "kind": "automatic",
            #     "credentials": {
            #         "enabled": False,
            #         "username": "test",
            #         "password": "test"
            #     }
            # },
            # # 401认证
            # "authentication": {
            #     "enabled": False,
            #     "username": "test",
            #     "password": "test"
            # }
        }
        if cookie:
            data["custom_cookies"] = [{"url": url, "cookie": cookie}]
        if proxy:
            url_parts = urlparse(proxy)
            data["proxy"] = {
                "enabled": True,
                "address": url_parts.hostname,
                "protocol": url_parts.scheme,
                "port": url_parts.port,
            }

        target_id = self.add_task(url)

        response = requests.patch(self.awvs_host_address + "api/v1/targets/" + str(target_id) + "/configuration",
                       data=json.dumps(data),
                       headers=self.awvs_header,
                       cookies=self.awvs_cookies,
                       timeout=30 * 4, verify=False)

        data = {"target_id": target_id, "profile_id": "11111111-1111-1111-1111-111111111117",
                "schedule": {"disable": False, "start_date": None, "time_sensitive": False}}
        try:
            response = requests.post(self.awvs_host_address + "api/v1/scans", data=json.dumps(data),
                                     headers=self.awvs_header,
                                     cookies=self.awvs_cookies,
                                     timeout=30,
                                     verify=False)

            result = json.loads(response.content)

            return result['target_id']
        except Exception as e:
            print("[-] Error: %s" % e)
            return

    def get_scan_id(self, target_id):
        try:
            response = requests.get(f"{self.awvs_host_address}api/v1/targets/{target_id}",
                                    headers=self.awvs_header, cookies=self.awvs_cookies, verify=False)
            results = json.loads(response.content)

            return results["last_scan_id"]

        except Exception as e:
            print("[-] Error:", str(e))

            return False

    def get_scan_status(self, scan_id):
        # 获取scan_id的扫描状况
        try:
            response = requests.get(self.awvs_host_address + "api/v1/scans/" + str(scan_id), headers=self.awvs_header,
                                    cookies=self.awvs_cookies,
                                    timeout=30, verify=False)
            result = json.loads(response.content)

            status = result['current_session']['status']

            # 如果是completed 表示结束.可以生成报告
            if status == "completed" or status == "failed":
                """
                info = {'criticality': 10, 'current_session': {'event_level': 0, 'progress': 0,
                                                               'scan_session_id': 'b5ed8b4b-7551-4258-b411-b43a86db6d11',
                                                               'severity_counts': {'high': 0, 'info': 0, 'low': 0,
                                                                                   'medium': 0},
                                                               'start_date': '2020-01-29T02:54:22.423351+00:00',
                                                               'status': 'completed', 'threat': 0},
                        'manual_intervention': False, 'next_run': None,
                        'profile_id': '11111111-1111-1111-1111-111111111111', 'profile_name': 'Full Scan',
                        'report_template_id': None, 'scan_id': 'd564f6c4-4542-4ce9-8c2f-38768d0d130a',
                        'schedule': {'disable': False, 'history_limit': None, 'recurrence': None, 'start_date': None,
                                     'time_sensitive': False},
                        'target': {'address': 'http://127.0.0.1', 'criticality': 10, 'description': 'http://127.0.0.1',
                                   'type': 'default'}, 'target_id': '08d77f26-312e-4710-a585-767160976acb'}
                """
                self.id_map_list.append({"scan_id": result["scan_id"], "target_id": result["target_id"]})
                return True
            else:
                return False
        except Exception as e:
            print("[-] Error:", str(e))
            return False

    def generate_reports(self, scan_ids):
        """
        生成scan_ids列表指定的scan_id的扫描报告，返回报告地址，如/api/v1/reports/10f2735b-1264-44cc-bab8-a112b1c7ccea

        template_id参数指定报告模板
        11111111-1111-1111-1111-111111111115    Affectd Items
        11111111-1111-1111-1111-111111111111    Developer
        21111111-1111-1111-1111-111111111111    XML
        11111111-1111-1111-1111-111111111119    OWASP Top 10 2013
        11111111-1111-1111-1111-111111111112    Quick
        """
        data = {"template_id": "11111111-1111-1111-1111-111111111115",
                "source": {"list_type": "scans", "id_list": scan_ids}}
        try:
            response = requests.post(self.awvs_host_address + "/api/v1/reports", data=json.dumps(data), headers=self.awvs_header,
                                     cookies=self.awvs_cookies,
                                     timeout=30,
                                     verify=False)

            result = response.headers["Location"]
            return result

        except Exception as e:
            print("[-] Error: %s" % repr(e))
            return

    def get_download_address(self, report_url):
        """
        根据报告地址获取下载连接
        :param report_url: /api/v1/reports/cdff6a34-eefa-42c7-89ce-6f80c5041436
        :return:
        """

        try:
            try_count = 10
            while try_count > 0:
                response = requests.get(self.awvs_host_address + report_url,
                                        headers=self.awvs_header,
                                        cookies=self.awvs_cookies,
                                        verify=False)

                if json.loads(response.content)["status"] != "completed":
                    try_count -= 1
                    # 需要等报告生成完成
                    time.sleep(3)
                else:
                    return json.loads(response.content)["download"][1], json.loads(response.content)["report_id"]

            return None, None
        except Exception as e:
            print("[-] Error: %s" % e)
            return None, None

    def download_report(self, download_url, path):
        response = requests.get(self.awvs_host_address + download_url, stream=True, headers=self.awvs_header, cookies=self.awvs_cookies, verify=False)
        path = path.replace("\\", "/")
        with open(path, 'wb') as f:
            f.write(response.content)
        return True

    def delete_task(self, scan_id):
        # 删除scan_id的扫描
        try:
            response = requests.delete(self.awvs_host_address + "/api/v1/scans/" + str(scan_id), headers=self.awvs_header,
                                       cookies=self.awvs_cookies,
                                       timeout=30,
                                       verify=False)
            # 如果是204 表示删除成功
            if response.status_code == 204:
                return True
            else:
                return False
        except Exception as e:
            print("[-] Error:", str(e))
            return

    def delete_target(self, target_id):
        # 删除target
        try:
            response = requests.delete(self.awvs_host_address + "api/v1/targets/" + str(target_id), headers=self.awvs_header,
                                       cookies=self.awvs_cookies,
                                       timeout=30,
                                       verify=False)
            # 如果是204 表示删除成功
            if response.status_code == 204:
                return True
            else:
                return False
        except Exception as e:
            print("[-] Error:", str(e))
            return

    def get_all_status(self):
        # 获取全部的扫描状态
        try:
            response = requests.get(self.awvs_host_address + "api/v1/scans", headers=self.awvs_header,
                                    cookies=self.awvs_cookies,
                                    timeout=30, verify=False)
            results = json.loads(response.content)
            """返回结果示例
            {
                "pagination":{
                    "count":4,
                    "cursor_hash":"8f629dd49f910b9202eb0da5d51fdb6e",
                    "cursors":[
                        null
                    ],
                    "sort":null
                },
                "scans":[
                    {
                        "criticality":10,
                        "current_session":{
                            "event_level":1,
                            "progress":0,
                            "scan_session_id":"8cb1f311-fd51-4745-bc1e-4d02eb17d5e8",
                            "severity_counts":{
                                "high":0,
                                "info":0,
                                "low":0,
                                "medium":0
                            },
                            "start_date":"2020-04-09T03:03:30.542898+00:00",
                            "status":"processing",
                            "threat":0
                        },
                        "incremental":false,
                        "max_scan_time":0,
                        "next_run":null,
                        "profile_id":"11111111-1111-1111-1111-111111111112",
                        "profile_name":"High Risk Vulnerabilities",
                        "report_template_id":null,
                        "scan_id":"68526115-545b-4a0a-96ba-c30ffd3a320a",
                        "schedule":{
                            "disable":false,
                            "history_limit":null,
                            "recurrence":null,
                            "start_date":null,
                            "time_sensitive":false,
                            "triggerable":false
                        },
                        "target":{
                            "address":"https://xxx.com",
                            "criticality":10,
                            "description":"https://xxx.com",
                            "type":"default"
                        },
                        "target_id":"424fce9a-efa8-4b31-82d6-6ddffc2f8a80"
                    }
                ]
            }
            """

            return results
        except Exception as e:
            print("[-] Error:", str(e))
            return None


def usage():
    print("Usage: \n\t{prog} add awvs_address urls_file output_dir xray_host xray_ports"
          "\n\t{prog} save awvs_address output_dir"
          "\n\t{prog} status awvs_address"
          "\neg:"
          "\n\t{prog} add https://127.0.0.1:3443/ ./urls.txt ./output/ 127.0.0.1 7621,7622,7623"
          "\n\t{prog} save https://127.0.0.1:3443/ ./output/"
          "\n\t{prog} status https://127.0.0.1:3443/".format(prog=sys.argv[0]))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        usage()
        exit(1)

    if sys.argv[1] == "add":
        # 添加target
        if len(sys.argv) < 7:
            usage()
            exit(1)

        awvs_host_address = sys.argv[2]
        awvs = AWVS(awvs_host_address)
        result = awvs.login()
        if not result:
            print("[-] Login awvs error")
            exit(1)

        domains_file_path = sys.argv[3]
        if not os.path.isfile(domains_file_path):
            print("[-] File %s not exist." % domains_file_path)
            exit(1)

        output_dir = sys.argv[4]
        domains_done_file_path = os.path.join(output_dir, "urls_done.txt")
        xray_host = sys.argv[5]
        xray_ports = sys.argv[6].split(",")

        domains_done = []
        if os.path.isfile(domains_done_file_path):
            with open(domains_done_file_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        domains_done.append(line)

        count = 0
        with open(domains_file_path, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    parts = line.split("::", 1)
                    url = line.split("::", 1)[0]
                    cookie = None
                    if len(parts) > 1:
                        cookie = parts[1]

                    if url in domains_done:
                        continue

                    if count >= len(xray_ports):
                        break

                    proxy = "http://%s:%s" %(xray_host, xray_ports[count])
                    print("[*] add target %s to xray(%s)" % (url, xray_ports[count]))
                    target_id = awvs.start_task(url, cookie=cookie, proxy=proxy)
                    if target_id:
                        count += 1
                        with open(domains_done_file_path, "a") as f_done:
                            f_done.write(url + "\n")
                    else:
                        print("[-] Add %s failed" % url)

    elif sys.argv[1] == "save":
        # 保存报告，删除已扫描完成的scan、target
        if len(sys.argv) < 4:
            usage()
            exit(1)

        awvs_host_address = sys.argv[2]
        awvs = AWVS(awvs_host_address)
        result = awvs.login()
        if not result:
            print("[-] Login awvs error")
            exit(1)

        output_dir = sys.argv[3]

        print("[*] Start Check scan status and download useful report")
        all_status = awvs.get_all_status()
        if all_status:
            scans = all_status.get("scans", [])
            for scan in scans:
                current_session = scan.get("current_session")
                status = current_session.get("status")
                scan_id = scan.get("scan_id")
                target = scan.get("target").get("address")
                target_id = scan.get("target_id")
                if status == "completed" or status == "aborted":
                    severity_counts = sum([c for c in current_session.get("severity_counts").values()])
                    if severity_counts > 0:
                        # 扫到漏洞，下载报告
                        report_url = awvs.generate_reports([scan_id])
                        download_url, report_id = awvs.get_download_address(report_url)
                        if download_url:
                            result = awvs.download_report(download_url, os.path.join(output_dir,  report_id + ".pdf"))
                            if result:
                                print("[+] download %s report successfully" % target)
                                # 删除scan、target与报告
                                result = awvs.delete_task(scan_id)
                                if result:
                                    print("[+] delete %s scan task successfully" % target)
                                else:
                                    print("[-] delete %s scan task failed" % target)

                                result = awvs.delete_target(target_id)
                                if result:
                                    print("[+] delete %s target successfully" % target)
                                else:
                                    print("[-] delete %s target failed" % target)
                                # TODO awvs.delete_report(report_id)

                        else:
                            print("[-] get_download_address(%s) failed" % target)
                    else:
                        # 没扫到漏洞，删除scan、target
                        result = awvs.delete_task(scan_id)
                        if result:
                            print("[+] delete %s scan task successfully" % target)
                        else:
                            print("[-] delete %s scan task failed" % target)

                        result = awvs.delete_target(target_id)
                        if result:
                            print("[+] delete %s target successfully" % target)
                        else:
                            print("[-] delete %s target failed" % target)
        else:
            print("[-] get_all_status failed")

        print("[*] Done")
    elif sys.argv[1] == "status":
        # 获取正在扫描的任务的个数
        if len(sys.argv) < 3:
            usage()
            exit(1)

        awvs_host_address = sys.argv[2]
        awvs = AWVS(awvs_host_address)
        result = awvs.login()
        if not result:
            print("[-] Login awvs error")
            exit(1)
        status = awvs.get_all_status()
        scanning = 0
        for scan in status.get("scans", []):
            if scan.get("current_session", {}).get("status", "") == "processing":
                scanning += 1
        print(scanning)






