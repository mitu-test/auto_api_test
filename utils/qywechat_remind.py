# -*- coding: utf-8 -*-
"""
@Time ： 2024/4/29 17:59
@Auth ： jun.guo
@File ：qywechat_remind.py
@IDE ：PyCharm
"""
import json
from datetime import datetime
import jenkins
import requests
import jmespath

host = "http://localhost:8080/"
username = 'admin'
password = 'niotest123456'
webhook = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=f4959107-c1d3-47f2-be78-098f80c2d194"
job = "auto_api_test"
server = jenkins.Jenkins(host, username=username, password=password)
last_build_number = server.get_job_info(job)['lastCompletedBuild']['number']
build_info = server.get_build_info(job, last_build_number)
print("构建信息：", build_info)
console_url = build_info['url'] + "console"
print("console:", console_url)
report_url = build_info['url'] + 'allure'
# report_url = ip_host + report_url.split(":")[-1]
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

# 使用Jenkins API token 模拟登录
USERNAME = "admin"
# Jenkins API token
TOKEN = "113b81ae7fd66046859f1b9833d391621a"
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

data = {
    "msgtype": "markdown",
    "markdown": {
        "content":
            f"""<font color="">钉钉oapi接口测试报告</font>
        >【用例总数】:<font color="comment">{total}</font>
        >【测试通过】:<font color="info">{passed}</font>
        >【测试失败】:<font color="warning">{failed}</font>
        >【测试错误】<font color="comment">{error}</font>
        >【测试跳过】<font color="comment">{skipped}</font>
        >【测试耗时】:<font color="comment">{duration}s</font>
        >【测试时间】:<font color="comment">{build_time}</font>
        >【测试结果】:<font color={"info" if success else "warning"}>{"通过~" if success else "失败!"}</font>{chr(0x1f600) if success else chr(0x1f627)}
        >[Allure详细报告，请点击查看]({report_url})"""

    }
}
requests.post(url=webhook, json=data)
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
first_string = f"""<font color="">钉钉oapi接口测试报错信息汇总</font>"""

failed_info = f"""
        >【失败用例】:
        """
broken_info = f""" >【错误用例】:
        """
failed_string = ""
broken_string = ""
for url_info in url_list:
    if url_info["status"] == "failed":
        failed_string += f""" ><font color="comment">{url_info["name"]}</font>
        ><font color="info">[{url_info["message"]}]({url_info["url"]})</font>
        """
    elif url_info["status"] == "broken":
        broken_string += f"""><font color="comment">{url_info["name"]}</font>
        ><font color="info">[{url_info["message"]}]({url_info["url"]})</font>
        """
if not failed_string:
    failed_string = f"""><font color="comment">无</font>"""
if not broken_string:
    broken_string = f"""><font color="comment">无</font>"""
end_string = f""" 
>【报告地址】:
<font color="info">[Allure详细报告，请点击查看]({report_url})</font>
"""
all_string = first_string + failed_info + failed_string + broken_info + broken_string + end_string
data_mk = {
    "msgtype": "markdown",
    "markdown": {
        "content": all_string
    }
}
for author in author_list:
    if author in list(phone_mapping.keys()):
        phone_list.append(phone_mapping[author])
# print(phone_list)

data_tx = {
    "msgtype": "text",
    "text": {
        "content": "请相关同事及时跟进处理!",
        "mentioned_mobile_list": phone_list
    }
}

if not success:
    # 企业微信发送错误日志
    requests.post(url=webhook, json=data_mk)
    requests.post(url=webhook, json=data_tx)
