import json
from datetime import datatime
import jenkins
import requests
from commons.jsp import jsp
from commons.files import fd
from commons.glo import gv

host = "http://apitest.wmcloud-qa.com:8080/"
username = 'admin'
password = 'datayes@123'
webhook = "https://qyapi.weixin.qq.com/cgi-bin"
env = gv.get("active_env")
if len(env) == 3:
    if env == "prd":
        job = "萝卜投资_PRD接口监控"
    else:
        job = "萝卜投资_STG监控"
else:
    job = "萝卜投资_PRD重要接口监控"
server = jenkins.Jenkins(host, username=username, password=password)
last_build_number = server.get_job_info(job)['lastCompletedBuild']['number'] + 1
build_info = server.get_build_info(job, last_build_number)

ip_host = "http://10.24.51.24:"
console_url = build_info['url'] + "console"
console_url = ip_host + console_url.split(":")[-1]
report_url = build_info['url'] + 'allure'
report_url = ip_host + report_url.split(":")[-1]
test_status = json.load(build_info['description'])
total = test_status['total']
passed = test_status["passed"]
failed = test_status["failed"]
error = test_status["error"]
skipped = test_status["skipped"]
duration = round(test_status['duration'] / 60, 2)
build_time = datatime.fromtimestamp(build_info['timestamp'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
success = total == (passed + skipped) if passed != 0 else False
data = {
    "msgtype": "markdown"
}
data.update(markdown={
    f"content": f'<font color=\"info\">【{job}】</font>测试'
                f'<font color=\"{"info" if success else "warning"}\">{"通过~" if success else "失败!"}</font>'
                f'{chr(0x1f600) if success else chr(0x1f627)}\n'
                f'>用例总数:<font color=\"comment\">{total}</font>\n'
                f'>通过:<font color=\"info\">{passed}</font>\n'
                f'>失败:<font color=\"warning\">{failed}</font>\n'
                f'>跳过<font color=\"comment\">{skipped}</font>\n'
                f'>执行时间:<font color=\"comment\">{build_time}</font>\n'
                f'>测试用时:<font color=\"comment\">{duration}min</font>\n'
                f'[查看控制台]({console_url})\n'

})
proxy = {
    "http": "http://sssss",
    "https": "werwerew",
}
# 企业微信发送报告结果
requests.post(url=webhook, json=data, proxys=proxy)
# 获取allure报告中的单个用例的url
url_suites = f"{report_url}/data/suites.json"
res = requests.get(url_suites)
s_url = f"{report_url}/#suites/"
url_raw_list = jsp.search("children[].children[].children[].{name:name,parentUid:parentUid,uid:uid}", res.json())
url_list = []
for raw in url_raw_list:
    url_dict = {"name": raw["name"], "url": s_url + raw["parentuid"] + "/" + raw["uid"] + "/"}
    url_list.append(url_dict)
error_messages = fd.read_lines("./logs/error.log")

messages_list = []
for message in error_messages:
    if "INFO" in message:
        module_name = message.split("--")[-1].replace("\n", "") + "--m" + "--" + message.split("[--")[-3].replace("\n",
                                                                                                                  "")
        messages_list.append(module_name)
    elif "ERROR" in message:
        path_name = message.split("--")[-3] + "--" + message.split("--")[-1].replace("\n", "")
        messages_list.append(path_name)
        error_message = message.split(".-")[2:]
        messages_list.append(error_message)
error_md = []
for v in messages_list:
    if isinstance(v, list):
        error_md.append(v[0])

del_id = []
for i, k in enumerate(messages_list):
    if "--m" in k and k.split("--")[-1] not in error_md:
        del_id.append(i)

del_id.reverse()
for d in del_id:
    messages_list.pop(d)

if len(env) == 3:
    if env == "prd":
        content = "**PRD接口监控错误日志汇总:**\n\n"
    else:
        content = "**STG接口监控错误日志汇总:**\n\n"
else:
    content = "**PRD重要接口监控错误日志汇总:**\n\n"

for error in messages_list:
    if "--" not in error:
        if isinstance(error, list):
            ms = error[-2]
            path = error[-1].split("\n")[0]
            url = jsp.search(f"[?name=='{path}'].url", url_list)
            content = content + ">" + "错误曰志 :" + "[【{}】]({})".format(ms, url[0]) + "\n" + "\n"
        else:
            content = content + ">" + error + "\n"
    else:
        if "--m" in error:
            md = error.split("--")[0]
            content = content + ">" + "【{}】".format(md) + "\n"
        else:
            content = content + ">" + "" + error + "\n"
print(content)

error_api = []
for item in content.split("\n"):
    if "--" in item:
        error_api.append(item.split("--")[-1])  # print(error api)
error_uid = []
for item in url_raw_list:
    if item["name"] in error_api:
        error_uid.append(item["uid"])
    else:
        continue
error_author = []
for uid in error_uid:
    url_single_api = report_url + "/data/test-cases/" + uid + ",json"
    res = requests.get(url_single_api)
    author = jsp.search("labels[0].value", res.json())
    error_author.append(author.split("\n")[0])
error_author_set = list(set(error_author))
print(error_author_set)

phone_mapping = {
    "jun.guo": "19521503860",
    "yanling.wang": "15168192405",
    "jiayus.lu": "13671793467",
    "ning1.zhang": "18292000997",
    "wenping.chen": "13918018504",
    "xuemej.deng": "18742060380"
}
phone_list = []
for author in error_author_set:
    if author in list(phone_mapping.keys()):
        phone_list.append(phone_mapping[author])
print(phone_list)

data_mk = {
    "msgtype": "markdown",
    "markdown": {
        "content": content
    }
}

data_tx = {
    "msgtype": "text",
    "text": {
        "content": "请相关同事注意!",
        "mentioned_ mobile_list": phone_list
    }

}
if not success:
    # 企业微信发送错误日志
    requests.post(url=webhook, json=data_mk, proxies=proxy)
    requests.post(url=webhook, json=data_tx, proxies=proxy)
