# -*- coding: utf-8 -*-
"""
@Time ： 2024/4/22 19:00
@Auth ： jun.guo
@File ：dingtalk_remind.py
@IDE ：PyCharm
"""
import json
from datetime import datetime
import jenkins
import requests

host = "http://localhost:8080/"
username = 'admin'
password = 'niotest123456'
webhook = "https://oapi.dingtalk.com/robot/send?access_token=bffb1003f5b0ac9d9be5f8c863a38e2d646a69cd231147524829ffbba10e0fa3"
job = "auto_api_test"
server = jenkins.Jenkins(host, username=username, password=password)
last_build_number = server.get_job_info(job)['lastCompletedBuild']['number']
build_info = server.get_build_info(job, last_build_number)
print("构建信息：",build_info)
console_url = build_info['url'] + "console"
print("console:",console_url)
report_url = build_info['url'] + 'allure'
print("report_url:",report_url)
test_status = json.loads(build_info['description'])
print("测试结果：",test_status)
total = test_status["total"]
passed = test_status["passed"]
failed = test_status["failed"]
error = test_status["error"]
skipped = test_status["skipped"]
duration = test_status["duration"]
build_time = datetime.fromtimestamp(build_info['timestamp'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
success = total == (passed + skipped) if passed != 0 else False
red = "#FF0000"
green = "#00ff00"
payload = json.dumps({
    "at": {
        "isAtAll": "true",
        "atUserIds": [
            "0113005751430150226"
        ],
        "atMobiles": []
    },
    "actionCard": {
        "title": "钉钉oapi接口测试报告",
        "text": f"**钉钉oapi接口测试报告** \n\n 【用例总数】：{total}\n\n 【测试通过】：<font color={green}>{passed}</font>\n\n 【测试失败】：<font color={red}>{failed}</font>\n\n 【测试错误】：{error}\n\n 【测试跳过】：{skipped}\n\n 【测试耗时】：{duration}s\n\n 【测试时间】：{build_time}\n\n【测试结果】：<font color={green if success else red}>{'通过~' if success else '失败!'}</font> {chr(0x1f600) if success else chr(0x1f627)}\n\n",
        "btnOrientation": "10",
        "singleTitle": "Allure详细报告，请点击查看",
        "singleURL": report_url
    },
    "msgtype": "actionCard"
})
headers = {
    'Content-Type': 'application/json'
}

response = requests.request("POST", webhook, headers=headers, data=payload)

print(response.json())
