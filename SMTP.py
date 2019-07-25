#!/usr/bin/python3
# -*- coding:utf-8 -*-
# 参考：https://www.runoob.com/python3/python3-smtp.html

import smtplib
from email.mime.text import MIMEText
from email.header import Header

class eMail:
    def sendEmail(self,txt):
        mail_host = "smtp.XXX.com" #设置服务器
        mail_user = "XXX" #用户名
        mail_pass = "XXX" #口令

        sender = 'XXX' #用户名
        receivers = ['XXX'] #接收邮件，可设置为你的QQ邮箱或者其他邮箱

        message = MIMEText(txt, 'plain', 'utf-8')
        message['From'] = Header("YangtzeuBot", 'utf-8')
        message['To'] = Header("One", 'utf-8')

        subject = '叮~有新成绩出炉！'
        message['Subject'] = Header(subject, 'utf-8')

        try:
            smtpObj = smtplib.SMTP()
            smtpObj.connect(mail_host, 25) #25 为 SMTP 端口号
            smtpObj.login(mail_user, mail_pass)
            smtpObj.sendmail(sender, receivers, message.as_string())
            print("邮件发送成功")
            smtpObj.quit()
        except smtplib.SMTPException:
            print("Error: 无法发送邮件")
            pass