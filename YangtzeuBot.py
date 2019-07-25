#!/usr/bin/python3
# -*- coding:utf-8 -*-

import re
import requests_html
from requests_html import HTMLSession
from Crypto.Hash import SHA1
from time import sleep
import xlwt
import getpass
import sys
# import execjs
from SMTP import *

class yangtzeuBot:
    def __init__(self):
        self.session = HTMLSession()
        self.url = 'http://221.233.24.23/eams/login.action'
        self.headers = {
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
            }
        self.examInfo = {}
        self.salt = None
        self.excel = None
        self.sheet = None
        self.semesterId = '69' #学期ID
        self.flag = 9 #本学期已经公布的成绩数目
        self.eMail = eMail()

    #获取登陆页面随机字符串
    def getSalt(self):
        response: requests_html.HTMLResponse = self.session.get(self.url,headers=self.headers)
        # salt = re.search(r"CryptoJS.SHA1\(\'.+[-]\'", response.text).group(0).split('\'')[1]
        salt = response.html.search("CryptoJS.SHA1('{}'")[0]
        return salt

    # 获取用于加密的JS脚本内容
    # def getJs(self):
    #     f = open("lib/sha1.js", 'r', encoding='utf-8')
    #     line = f.readline()
    #     htmlstr = ''
    #     while line:
    #         htmlstr = htmlstr+line
    #         line = f.readline()
    #     return htmlstr
    # 加密（JS）
    # def getSha1Pwd(self, key):
    #     jsStr = self.getJs()
    #     jsIni = execjs.compile(jsStr)
    #     data = self.salt+key
    #     # pwd = jsIni.call('CryptoJS.SHA1', data)
    #     pwd = jsIni.call('sha1PwdtoStr', data)
    #     return pwd

    #加密
    def getSha1Pwd(self, key):
        sha1Encode = SHA1.new()
        pwd = self.salt+key
        pwd = pwd.encode('utf-8')
        sha1Encode.update(pwd)
        pwd = sha1Encode.hexdigest()
        return pwd

    #登陆
    def login(self, id, key):
        if id is '':
            print("\n用户名不能为空！\n")
            sys.exit()
        self.salt = self.getSalt()
        pwd = self.getSha1Pwd(key)
        loginData = {
            'username': id,
            'password': pwd,
        }
        sleep(1)
        response: requests_html.HTMLResponse = self.session.post(self.url,headers = self.headers,data = loginData)
        status = response.html.xpath("//*[contains(@id,'messages')]/div/div/span[2]")
        if len(status) is 0:
            print("\n登陆成功！\n")
        else:
            print('\n' + status[0].text + '！\n')
            sys.exit()

    #获取本学期成绩，有新成绩时自动发邮件通知（2018-2019 下学期）
    def getScore(self):
        url = 'http://221.233.24.23/eams/teach/grade/course/person!search.action?semesterId=' + self.semesterId
        response: requests_html.HTMLResponse = self.session.get(url,headers = self.headers)
        coursePath = "//*[contains(@id,'grid')]/tr"
        courseNum = len(response.html.xpath(coursePath))
        txt = ''
        if courseNum > self.flag or self.examInfo == {}:
            for i in range(courseNum):
                coursePath = "//*[contains(@id,'grid')]/tr[" + str(i+1) + "]/td[4]"
                scorePath = "//*[contains(@id,'grid')]/tr[" + str(i+1) + "]/td[8]"
                getCourse: requests_html.Element = response.html.xpath(coursePath)[0]
                getScore: requests_html.Element = response.html.xpath(scorePath)[0]
                if self.examInfo.get(getCourse) is None:
                    self.examInfo[getCourse.text] = getScore.text
                    # txt = getCourse.text+':'+getScore.text #最新公布的单科成绩
            if courseNum > self.flag:
                self.flag = courseNum
                for dict_key, dict_value in self.examInfo.items():
                    txt += dict_key+':'+dict_value+'\n' #本学期已公布的全部成绩
                print(txt)
                # print('The new score.')
                # self.eMail.sendEmail(txt) #邮件通知

    #获取全部成绩
    def getAllScore(self):
        url = 'http://221.233.24.23/eams/teach/grade/course/person!historyCourseGrade.action?projectType=MAJOR'
        response: requests_html.HTMLResponse = self.session.get(url, headers = self.headers)
        coursePath = "//*[contains(@id,'grid')]/tr"
        courseNum = len(response.html.xpath(coursePath))
        for i in range(courseNum):
            coursePath = "//*[contains(@id,'grid')]/tr[" + str(i+1) + "]/td[4]"
            scorePath = "//*[contains(@id,'grid')]/tr[" + str(i+1) + "]/td[8]"
            getCourse: requests_html.Element = response.html.xpath(coursePath)[0]
            getScore: requests_html.Element = response.html.xpath(scorePath)[0]
            print(getCourse.text+':'+getScore.text)

    #课程表excel初始化
    def tablelIni(self):
        date = ('', '一', '二', '三', '四', '五', '六', '日')
        self.excel = xlwt.Workbook(encoding='utf-8',style_compression=0)
        self.sheet = self.excel.add_sheet('Course', cell_overwrite_ok=True)
        self.sheet.write(0, 0, '节次/周次')
        for i in range(1, len(date)-1):
            self.sheet.write(i, 0, '第'+date[i]+'节')
        self.sheet.write(7, 0, '午间课')
        self.sheet.write(8, 0, '晚间课')
        for i in range(1, len(date)):
            self.sheet.write(0, i, '星期'+date[i])

    #获取课程表
    def getTable(self):
        url = 'http://221.233.24.23/eams/courseTableForStd!courseTable.action'
        tableData = {
            'semester.id':self.semesterId,
            'setting.kind':'std',
            'ignoreHead':1,
            'ids':455092,
            'project.id': 1
        }
        response: requests_html.HTMLResponse = self.session.post(url, headers = self.headers,  data = tableData)
        column = response.html.search_all("index ={}")[1:]
        row = response.html.search_all("unitCount+{}")
        course = response.html.search_all("new TaskActivity(actTeacherId.join(','),actTeacherName.join(','),{});")
        self.tablelIni()
        for i in range(len(course)):
            txt = course[i][0].split('"')[3].split('(')[0] + chr(10) + course[i][0].split('"')[7]
            self.sheet.write(int(row[i][0])+1, int(column[i][0])+1, txt)
        try:
            self.excel.save('C:/Users/OneLee/Desktop/Schedule.xls')
            print('课程表已生成')
        except Exception as e:
            print(e)


if __name__ == '__main__':
    bot = yangtzeuBot()
    # id = input("用户名：")
    # pwd = input("密码:")
    # pwd = getpass.getpass("密码:") #输入时隐藏输入内容（Pycharm不兼容，需要Terminal运行）
    # bot.login(id, pwd)
    bot.login('', '')
    bot.getScore()
    # bot.getAllScore()
    # bot.getTable()
    '''
    i = 1
    print('******')
    while True:
        if i == 10:
            bot.login('', '') #查询十次后重新登陆
            i = 1
            print('******')
        print("No.", i)
        bot.getScore()
        i = i+1
        sleep(600) #cookie时效性为十五分钟左右，这里设置为十分钟查询一次
    # '''