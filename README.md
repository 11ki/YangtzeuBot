# 长江大学（Yangtzeu）教务系统爬虫
## 相关模块
import requests_html：主要用到的模块，用来进行http请求，HTMLSession用来自动处理Cookie
from Crypto.Hash import SHA1：加密
from time import sleep：延时
import xlwt：用来把数据保存为excel格式
import re：正则
import getpass：输入时隐藏输入内容
import sys：与解释器交互， sys.exit()用来退出Python程序
import smtplib：发送邮件
## 登陆分析

 - 查看POST登陆时提交的表单

> username: 2018*****
password:c06c7d1627098d4be9e66ebb8dc3626ee38a4946
encodedPassword:  
session_locale: zh_CN

用户名为明文，密码是加密的

 - 查看登陆界面源码寻找密码加密方式
```javascript
<script type="text/javascript">
	var form  = document.loginForm;

	function checkLogin(form){
		if(!form['username'].value){
			alert("用户名称不能为空");return false;
		}
		if(!form['password'].value){
			alert("密码不能为空");return false;
		}
    	form['password'].value = CryptoJS.SHA1('1942e417-14b1-419e-9524-124448de3966-' + form['password'].value);
		return true;
	}
```
可以看出是通过CryptoJS.SHA1（随机字符串+明文密码）这个函数调用JS加密，分析可知这个随机字符串是后台返回的值
JS：http://221.233.24.23/eams/static/scripts/sha1.js
 - 两种解决方法
 1. Python中调用JS进行加密`import execjs`；（这个模块需要用到node.js）
 2. 用Python中与JS加密方式相同的模块进行加密`from Crypto.Hash import SHA1`；（推荐）
- 登陆

构建表单，POST后的登陆状态不能用Status Code判断，需要获取返回的网页源码中的某个标签来进行判断
## 服务器部署
 - Linux端用screen命令后台运行程序，为了更方便的查看screen的日志文件，在配置文件`/etc/screenrc`中添加如下内容：`logfile /tmp/screenlog/%t.log`，这样就确保了每个screen会话窗口都有单独的日志文件。
 - 然后通过命令`screen -L -t bot -dmS bots yangtzeuBot`启动程序（注意此处的yangtzeuBot为程序路径，如果没有事先进行软链接要替换为绝对路径），这条语句的意思是“启动bots会话运行yangtzeuBot程序 ，窗口名为bot，日志文件路径为`/tmp/screenlog/bot.log`”，程序运行后我们就可以在日志文件中看到主程序Print语句打印的内容或者是报错信息。
## 课程表接口分析
 - 可以看出是POST登陆：
 > Request URL: http://221.233.24.23/eams/courseTableForStd!courseTable.action
Request Method: POST
Status Code: 200 OK
Remote Address: 221.233.24.23:80
Referrer Policy: no-referrer-when-downgrade
 - 表单内容为：
> ignoreHead: 1
setting.kind: std （课表类型，个人课表或者班级课表）
startWeek: 
semester.id: 69（学期ID）
ids: 455092
- 接口源码：
```javascript
<script language="JavaScript">
	// function CourseTable in TaskActivity.js
	var language = "zh";
	var table0 = new CourseTable(2019,56);
	var unitCount = 8;
	var index=0;
	var activity=null;
	
	...
	
		for (var i = 0; i < actTeachers.length; i++) {
			actTeacherId.push(actTeachers[i].id);
			actTeacherName.push(actTeachers[i].name);
		}
			activity = new TaskActivity(actTeacherId.join(','),actTeacherName.join(','),"112007(437468)","数值分析(437468)","114","东13-D-225c","01111111111111111110000000000000000000000000000000000",null,null,assistantName,"","");
			index =0*unitCount+3;
			table0.activities[index][table0.activities[index].length]=activity;
```
可以看出是通过JS填充的课表，分析后可知`index =0*unitCount+3;`中的两个数字即为这门学科在课程表中的坐标，第一个数字为列号，第二个数字为行号。通过这个坐标可以知道这门学科是星期几的第几节课，在把抓取的课程表保存为Excel格式时也会用到。
## 相关接口
学期成绩：http://221.233.24.23/eams/teach/grade/course/person!search.action?semesterId=学期ID
全部成绩：http://221.233.24.23/eams/teach/grade/course/person!historyCourseGrade.action?projectType=MAJOR
考试信息：http://221.233.24.23/eams/stdExamTable!examTable.action?examBatch.id=学期ID
资格考试：http://221.233.24.23/eams/stdOtherExamSignUp.action
学籍信息：http://221.233.24.23/eams/stdDetail.action
学籍照片：http://221.233.24.23/eams/showSelfAvatar.action?user.name=学号
课程表（POST）：http://221.233.24.23/eams/courseTableForStd!courseTable.action
