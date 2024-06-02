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
import jmespath

host = "http://localhost:8081/"
username = 'admin'
password = 'niotest123456'
webhook = "https://oapi.dingtalk.com/robot/send?access_token=bffb1003f5b0ac9d9be5f8c863a38e2d646a69cd231147524829ffbba10e0fa3"
env = "test"
stage = "回归测试"
job = "auto_test_api"
maintainer = "米兔1号"
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
passed_ratio = round(passed / total, 4) * 100
print("passed_ratio", passed_ratio)
failed = test_status["failed"]
failed_ratio = round((100 - passed_ratio),2)
print("failed:", failed_ratio)
error = test_status["error"]
skipped = test_status["skipped"]
duration = test_status["duration"]
build_time = datetime.fromtimestamp(build_info['timestamp'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
success = total == (passed + skipped) if passed != 0 else False

# 使用Jenkins API token 模拟登录
USERNAME = "admin"
# Jenkins API token
TOKEN = "118bfff6c447ee06c6d70684f6686bd42e"
url_suites = f"{report_url}/data/suites.json"
print("url_suites", url_suites)
res = requests.get(url_suites, auth=(USERNAME, TOKEN))
print("res", res)
s_url = f"{report_url}/#suites/"
print('s_url', s_url)
url_raw_list = jmespath.search(
    "children[].children[].children[].children[?status=='failed'||status=='broken'].{name:name,parentUid:parentUid,uid:uid,status:status,tags:tags}",
    res.json())
print("url_raw_list", url_raw_list)

url_list = []
for raw in url_raw_list[0]:
    url_dict = {"name": raw["name"], "url": s_url + raw["parentUid"] + "/" + raw["uid"] + "/", "uid": raw["uid"],
                "status": raw["status"], "author": raw["tags"][0]}
    url_list.append(url_dict)
# print("url_list", url_list)


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
        "title": "钉钉oapi接口测试任务执行报告通知",
        "text": f"**钉钉oapi接口测试任务执行报告通知** \n\n -**任务名称**：{job}\n\n -**测试阶段**：{stage}\n\n-**测试结果**：<font color={green if success else red}>{'通过~' if success else '失败!'}</font> {chr(0x1f600) if success else chr(0x1f627)}\n\n-**用例总数**：{total}\n\n -**通过数**：<font color={green}>{passed}</font>\n\n-**通过率**：{passed_ratio}%\n\n-**失败数**：<font color={red}>{failed}</font>\n\n-**失败率**：{failed_ratio}%\n\n -**错误数**：{error}\n\n -**跳过数**：{skipped}\n\n -**执行人**：@{maintainer}\n\n-**执行时间**：{build_time}\n\n-**执行耗时**：{duration}s\n\n",
        "btnOrientation": "10",
        "singleTitle": "查看测试报告",
        "singleURL": report_url
    },
    "msgtype": "actionCard"
})
headers = {
    'Content-Type': 'application/json'
}

response = requests.request("POST", webhook, headers=headers, data=payload)

print(response.json())
# 单个报告，详细数据
# http://localhost:8080/job/auto_api_test/76/allure/data/test-cases/9a4eba68509440c8.json

phone_mapping = {
    "jun.guo": "19521503860",
    "jim.guo": "17764591649"
}
single_url = f"{report_url}/data/test-cases/"
for case in url_list:
    url = single_url + str(case["uid"]) + ".json"
    res = requests.get(url, auth=(USERNAME, TOKEN)).json()
    case["message"] = res["statusMessage"]
print("url_list", url_list)
author_list = list(set(jmespath.search("[*].author", url_list)))
# print("author_list",author_list)
failed_list = jmespath.search("[?status=='failed']", url_list)
print("failed_list", failed_list)
broken_list = jmespath.search("[?status=='broken']", url_list)
print("broken_list", broken_list)
phone_list = []
first_string = f"""**钉钉oapi接口测试任务执行错误日志通知** \n\n"""
failed_info = f"""【**失败用例**】:"""
broken_info = f"""\n\n【**错误用例**】:"""
failed_string = ""
broken_string = ""
for url_info in url_list:
    if url_info["status"] == "failed":
        failed_string += f"""\n\n{url_info["name"]}\n\n [{url_info["message"]}]({url_info["url"]})\n\n@{phone_mapping[url_info["author"]]}"""
    elif url_info["status"] == "broken":
        broken_string += f"""\n\n{url_info["name"]}\n\n [{url_info["message"]}]({url_info["url"]})\n\n@{phone_mapping[url_info["author"]]}"""
if not failed_string:
    failed_string = f"\n\n无"
if not broken_string:
    broken_string = f"\n\n无"
end_string = f""
all_string = first_string + failed_info + failed_string + broken_info + broken_string + end_string
for author in author_list:
    if author in list(phone_mapping.keys()):
        phone_list.append(phone_mapping[author])
# print(phone_list)
data_ca = {
    "at": {
        "isAtAll": "false",
        "atUserIds": [],
        "atMobiles": phone_list
    },
    "actionCard": {
        "title": "钉钉oapi接口测试报错信息汇总",
        "text": all_string,
        "btnOrientation": "10",
        "singleTitle": "查看测试报告",
        "singleURL": report_url
    },
    "msgtype": "actionCard"
}
response_r = requests.request("POST", webhook, headers=headers, data=json.dumps(data_ca))
print("response_r", response_r.json())
