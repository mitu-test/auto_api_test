# -*- coding: utf-8 -*-
"""
@Time ： 2024/5/6 17:31
@Auth ： jun.guo
@File ：email_remind.py
@IDE ：PyCharm
"""
import json
from datetime import datetime
import jenkins
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
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

# 设置邮箱地址】
mail_host = 'smtp.139.com'
# 设置用户名
mail_user = '19521503860@139.com'
# 设置密码
mail_pass = 'Niotest340826'

# 设置以哪个地址来发送
sender = '19521503860@139.com'
# 发给哪些人
receivers = ['17764591649@163.com']
# 设置文本，用到"from email.mime.text import MIMEText",'plain'格式，'utf-8'编码
message = MIMEText('你好', 'plain', 'utf-8')
# 邮件内容
message['Subject'] = '每日运行报告'
message['From'] = sender
message['To'] = receivers[0]

try:
    # 现在的邮箱一般都支持SSl安全协议,加密后端口为465，
    smtpObj = smtplib.SMTP_SSL(mail_host, 465)
    # 方便通过日志找异常原因
    smtpObj.set_debuglevel(1)
    # 登陆邮箱
    smtpObj.login(mail_user, mail_pass)
    # 发送
    smtpObj.sendmail(sender, receivers, message.as_string())
    # 退出/关闭发送邮箱
    smtpObj.quit()
    print("邮件发送成功")
# 捕捉异常
except smtplib.SMTPException as e:
    print('error', e)