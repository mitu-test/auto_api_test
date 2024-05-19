# -*- coding: utf-8 -*-
"""
@Time ： 2024/4/30 11:01
@Auth ： jun.guo
@File ：feishu_remind.py
@IDE ：PyCharm
"""
import json
from datetime import datetime
import jenkins
import requests

host = "http://localhost:8080/"
username = 'admin'
password = 'niotest123456'
webhook = "https://open.feishu.cn/open-apis/bot/v2/hook/c864de8a-cac3-4523-b234-85269cf4945d"
job = "auto_api_test"
server = jenkins.Jenkins(host, username=username, password=password)
last_build_number = server.get_job_info(job)['lastCompletedBuild']['number']
build_info = server.get_build_info(job, last_build_number)
print("构建信息：", build_info)
console_url = build_info['url'] + "console"
print("console:", console_url)
report_url = build_info['url'] + 'allure'
print("report_url:", report_url)
test_status = json.loads(build_info['description'])
print("测试结果：", test_status)
total = test_status["total"]
passed = test_status["passed"]
failed = test_status["failed"]
error = test_status["error"]
skipped = test_status["skipped"]
duration = test_status["duration"]
build_time = datetime.fromtimestamp(build_info['timestamp'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
success = total == (passed + skipped) if passed != 0 else False

url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"

payload = json.dumps({
  "app_id": "cli_a6baddbc63b4500c",
  "app_secret": "c39BkuRpZqbXzgcyab7fqgRVkTfT7skL"
})
headers = {
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload).json()
red = "#FF0000"
green = "#00ff00"
a = 'green'
payload = json.dumps({
    "msg_type": "post",
    "content": {
        "post": {
            "zh_cn": {
                "title": "钉钉oapi接口测试报告",
                "content": [
                    [
                        {
                            "tag": "text",
                            "text": f"【用例总数】:{total} \n"
                        },
                        {
                            "tag": "text",
                            "text": f"【测试通过】:{passed} \n"
                        },
                        {
                            "tag": "text",
                            "text": f"【测试失败】:{failed} \n"
                        },
                        {
                            "tag": "text",
                            "text": f"【测试错误】:{error} \n"
                        },
                        {
                            "tag": "text",
                            "text": f"【测试跳过】:{skipped} \n"
                        },
                        {
                            "tag": "text",
                            "text": f"【测试耗时】:{duration}s \n"
                        },
                        {
                            "tag": "text",
                            "text": f"【测试时间】:{build_time} \n"
                        },
                        {
                            "tag": "text",
                            "text": f"【测试结果】: {'通过~' if success else '失败!'}{chr(0x1f600) if success else chr(0x1f627)} \n"
                        },
                        {
                            "tag": "a",
                            "text": "Allure详细报告，请查看",
                            "href": f"{report_url}"
                        }
                    ]
                ]
            }
        }
    }
})
headers = {
  'Authorization': f"Bearer {response['tenant_access_token']}",
  'Content-Type': 'application/json'
}

requests.request("POST", webhook, headers=headers, data=payload)

