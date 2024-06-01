# -*- coding: utf-8 -*-
"""
@Time ： 2024/5/6 17:31
@Auth ： jun.guo
@File ：email_remind.py
@IDE ：PyCharm
"""
import json
import html
from datetime import datetime
import jenkins
import smtplib
from email.mime.text import MIMEText

host = "http://localhost:8080/"
username = 'admin'
password = 'niotest123456'
webhook = "https://oapi.dingtalk.com/robot/send?access_token=bffb1003f5b0ac9d9be5f8c863a38e2d646a69cd231147524829ffbba10e0fa3"
env = "test"
stage = "回归测试"
job = "auto_api_test"
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
failed_ratio = round((100 - passed_ratio), 2)
print("failed:", failed_ratio)
error = test_status["error"]
skipped = test_status["skipped"]
duration = test_status["duration"]
build_time = datetime.fromtimestamp(build_info['timestamp'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
success = total == (passed + skipped) if passed != 0 else False

sender = user = '1450655645@qq.com'  # 发送方的邮箱账号
passwd = 'yxpbjkrdupxugcbg'  # 授权码
receiver = '19521503860@139.com'  # 接收方的邮箱账号，不一定是QQ邮箱

# 读入 html 文件的内容
html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>钉钉oapi接口测试报告</title>
</head>
<body>
<h3>钉钉oapi接口测试报告</h3>
<li>【任务名称】：{job}</li>
<li>【测试阶段】：{stage}</li>
<li>【测试结果】：{'通过' if success else '失败'}</li>
<li>【用例总数】：{total}个</li>
<li>【通过数】：{passed}个</li>
<li>【通过率】：{passed_ratio}%</li>
<li>【失败数】：{failed}个</li>
<li>【失败率】：{failed_ratio}%</li>
<li>【错误数】：{error}个</li>
<li>【跳过数】：{skipped}个</li>
<li>【执行人】：{maintainer}</li>
<li>【执行时间】：{build_time}</li>
<li>【执行耗时】：{duration}</li>
<li><a href={report_url}>Allure详细报告,请点击查看</a></li>
<br>
（本邮件由系统自动发出,请勿回复！）
</body>
</html>
"""
print("html_content", html_content)
# with open('1.html', mode='r', encoding='utf-8') as f:
#     html_content = f.read()
# 指定类型是 html
msg = MIMEText(html_content, 'html', 'utf-8')
msg['From'] = user
msg['To'] = receiver
msg['Subject'] = '钉钉oapi接口测试任务执行报告通知'
smtp = smtplib.SMTP_SSL('smtp.qq.com', 465)
smtp.login(user, passwd)
smtp.sendmail(user, receiver, msg.as_string())
