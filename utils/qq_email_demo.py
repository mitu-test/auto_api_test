import smtplib
import time
from email.mime.text import MIMEText


def send_qq_email_plain():
    sender = user = '1450655645@qq.com'  # 发送方的邮箱账号
    passwd = 'yxpbjkrdupxugcbg'  # 授权码

    receiver = '19521503860@139.com'  # 接收方的邮箱账号，不一定是QQ邮箱

    # 纯文本内容
    msg = MIMEText(f'Python 邮件发送测试 {time.time()}', 'plain', 'utf-8')

    # From 的内容是有要求的，前面的abc为自己定义的 nickname，如果是ASCII格式，则可以直接写
    msg['From'] = f'abc <1450655645@qq.com>'
    msg['To'] = receiver
    msg['Subject'] = 'Python SMTP 邮件测试'  # 点开详情后的标题

    try:
        # 建立 SMTP 、SSL 的连接，连接发送方的邮箱服务器
        smtp = smtplib.SMTP_SSL('smtp.qq.com', 465)

        # 登录发送方的邮箱账号
        smtp.login(user, passwd)

        # 发送邮件 发送方，接收方，发送的内容
        smtp.sendmail(sender, receiver, msg.as_string())

        print('邮件发送成功')

        smtp.quit()
    except Exception as e:
        print(e)
        print('发送邮件失败')


def send_qq_mail_html():
    sender = user = '1450655645@qq.com'  # 发送方的邮箱账号
    passwd = 'yxpbjkrdupxugcbg'  # 授权码

    receiver = '19521503860@139.com'  # 接收方的邮箱账号，不一定是QQ邮箱

    # 直接写
    # html_content = '''
    #     <h1>这个是邮件的内容</h1>
    # '''

    # 读入 html 文件的内容
    with open('email_report.html', mode='r', encoding='utf-8') as f:
        html_content = f.read()

    # 指定类型是 html
    msg = MIMEText(html_content, 'html', 'utf-8')
    msg['From'] = user
    msg['To'] = receiver
    msg['Subject'] = '测试发送 HTML 内容'

    try:
        smtp = smtplib.SMTP_SSL('smtp.qq.com', 465)
        smtp.login(user, passwd)
        smtp.sendmail(user, receiver, msg.as_string())
        print('发送成功')
    except:
        print('发送失败')






if __name__ == '__main__':
    send_qq_email_plain()
    send_qq_mail_html()
