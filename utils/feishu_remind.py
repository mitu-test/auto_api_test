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
import jmespath

host = "http://localhost:8081/"
username = 'admin'
password = 'niotest123456'
webhook = "https://open.feishu.cn/open-apis/bot/v2/hook/c864de8a-cac3-4523-b234-85269cf4945d"
env = "test"
stage = "回归测试"
job = "auto_api_test"
maintainer = "米兔1号"
server = jenkins.Jenkins(host, username=username, password=password)
last_build_number = server.get_job_info(job)['lastCompletedBuild']['number'] +1
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
failed_ratio = round((100 - passed_ratio), 2)
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
# print("url_suites", url_suites)
res = requests.get(url_suites, auth=(USERNAME, TOKEN))
# print("res", res.content)
s_url = f"{report_url}/#suites/"
# print('s_url', s_url)
url_raw_list = jmespath.search(
    "children[].children[].children[].children[?status=='failed'||status=='broken'].{name:name,parentUid:parentUid,uid:uid,status:status,tags:tags}",
    res.json())
# print("url_raw_list", url_raw_list)

url_list = []
for raw in url_raw_list[0]:
    url_dict = {"name": raw["name"], "url": s_url + raw["parentUid"] + "/" + raw["uid"] + "/", "uid": raw["uid"],
                "status": raw["status"], "author": raw["tags"][0]}
    url_list.append(url_dict)
# print("url_list", url_list)

url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"

payload = json.dumps({
    "app_id": "cli_a6baddbc63b4500c",
    "app_secret": "c39BkuRpZqbXzgcyab7fqgRVkTfT7skL"
})
headers = {
    'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload).json()
# red = "#FF0000"
# green = "#00ff00"
a = 'green'
b = 'red'
c = 'yellow'
card_demo = {
    "msg_type": "interactive",
    "card": {
        "elements": [{
            "tag": "div",
            "text": {
                "content": f"-**任务名称**：{job}\n\n-**测试阶段**：{stage}\n\n-**测试结果**：<font color={a if success else b}>{'通过~' if success else '失败!'}</font> {chr(0x1f600) if success else chr(0x1f627)}\n\n-**用例总数**：{total}\n\n-**通过数**：<font color={a}>{passed}</font>\n\n-**通过率**：{passed_ratio}%\n\n-**失败数**：<font color={b}>{failed}</font>\n\n-**失败率**：{failed_ratio}%\n\n-**错误数**：{error}\n\n-**跳过数**：{skipped}\n\n-**执行人**：@{maintainer}\n\n-**执行时间**：{build_time}\n\n-**执行耗时**：{duration}s\n\n",
                "tag": "lark_md"
            }
        }, {
            "actions": [{
                "tag": "button",
                "text": {
                    "content": "查看测试报告",
                    "tag": "lark_md"
                },
                "url": report_url,
                "type": "primary",
                "value": {"key": "value"}
            }],
            "tag": "action"
        }],
        "header": {
            "template": "wathet",
            "title": {
                "content": "钉钉oapi接口测试任务执行报告通知",
                "tag": "plain_text"
            }
        }
    }
}

# payload = json.dumps({
#     "msg_type": "post",
#     "content": {
#         "post": {
#             "zh_cn": {
#                 "title": "钉钉oapi接口测试报告",
#                 "content": [
#                     [
#                         {
#                             "tag": "text",
#                             "text": f"【用例总数】:{total} \n"
#                         },
#                         {
#                             "tag": "text",
#                             "text": f"【测试通过】:{passed} \n"
#                         },
#                         {
#                             "tag": "text",
#                             "text": f"【测试失败】:{failed} \n"
#                         },
#                         {
#                             "tag": "text",
#                             "text": f"【测试错误】:{error} \n"
#                         },
#                         {
#                             "tag": "text",
#                             "text": f"【测试跳过】:{skipped} \n"
#                         },
#                         {
#                             "tag": "text",
#                             "text": f"【测试耗时】:{duration}s \n"
#                         },
#                         {
#                             "tag": "text",
#                             "text": f"【测试时间】:{build_time} \n"
#                         },
#                         {
#                             "tag": "text",
#                             "text": f"【测试结果】: {'通过~' if success else '失败!'}{chr(0x1f600) if success else chr(0x1f627)} \n"
#                         },
#                         {
#                             "tag": "a",
#                             "text": "Allure详细报告，请查看",
#                             "href": f"{report_url}"
#                         }
#                     ]
#                 ]
#             }
#         }
#     }
# })
payload = json.dumps(card_demo)

headers = {
    'Authorization': f"Bearer {response['tenant_access_token']}",
    'Content-Type': 'application/json'
}

requests.request("POST", webhook, headers=headers, data=payload)

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

failed_string = f"<font color={b}>【**失败用例**】:\n</font>"
broken_string = f"<font color={c}>【**错误用例**】:\n</font>"

for url_info in url_list:
    name_text = " " + url_info["name"] + "\n"
    url_text = "[" + " " + url_info["message"] + "]" + "(" + url_info["url"] + ")" + "\n"
    single_case_text = name_text + url_text
    # at_dict = {
    #     "tag": "at",
    #     "user_id": 1111,
    # }
    if url_info["status"] == "failed":
        failed_string += single_case_text
        # failed_string_list.append(url_dict)
        # failed_string_list.append(at_dict)
    elif url_info["status"] == "broken":
        failed_string += single_case_text

        # broken_string_list.append(name_dict)
        # broken_string_list.append(url_dict)
        # broken_string_list.append(at_dict)
null_string = " " + f"无\n"
if not failed_list:
    failed_string += null_string
if not broken_list:
    broken_string += null_string
# print("failed_string_list", failed_string_list, type(failed_string_list))
# print("broken_string_list", broken_string_list, type(broken_string_list))
# end_string_list = [{
#     "tag": "a",
#     "text": "Allure详细报告，请查看",
#     "href": f"{report_url}"
# }]
all_string = failed_string + broken_string
# print("all_string", all_string_list, type(all_string_list))

data_ca_demo = {
    "msg_type": "interactive",
    "card": {
        "elements": [{
            "tag": "div",
            "text": {
                "content": all_string,
                "tag": "lark_md"
            }
        }, {
            "actions": [{
                "tag": "button",
                "text": {
                    "content": "查看测试报告",
                    "tag": "lark_md"
                },
                "url": report_url,
                "type": "primary",
                "value": {"key": "value"}
            }],
            "tag": "action"
        }],
        "header": {
            "template": "wathet",
            "title": {
                "content": "钉钉oapi接口测试任务执行错误日志通知",
                "tag": "plain_text"
            }
        }
    }
}
# data_ca = {
#     "msg_type": "post",
#     "content": {
#         "post": {
#             "zh_cn": {
#                 "title": "钉钉oapi接口测试报错信息汇总",
#                 "content": all_string_list
#             }
#         }
#     }
# }
print("data_ca", data_ca_demo)
for author in author_list:
    if author in list(phone_mapping.keys()):
        phone_list.append(phone_mapping[author])
print(phone_list)

response_r = requests.request("POST", webhook, headers=headers, data=json.dumps(data_ca_demo))
print("response_r", response_r.json())
