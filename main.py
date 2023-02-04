# -*- coding: utf-8 -*-
import json
import time
import requests
import random
import sys
import os
import yagmail
import logging

# 记录成功打卡人数的标记
flag = 0


# 优先从当前目录下读取config.json文件，如果没有则从环境变量中读取
# 在当前目录下有config.json文件时，环境变量中的config变量将被忽略
try:
    with open(sys.path[0]+'/config.json', 'r', encoding='UTF-8') as f:
        jsonObj = json.loads(f.read())
        Account = jsonObj['account']
        STMPConfig = jsonObj['STMP']
        AdminEmail = jsonObj['AdminEmail']
except FileNotFoundError:
    conf = os.getenv('config')
    Account = (json.loads(conf))['account']
    STMPConfig = (json.loads(conf))['STMP']
    AdminEmail = (json.loads(conf))['AdminEmail']


# 配置输出log信息
# 创建一个logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# 创建一个handler，用于写入日志文件
fh_debug = logging.FileHandler(sys.path[0]+'/debug.log', encoding='utf8')
fh_debug.setLevel(logging.DEBUG)

fh_info = logging.FileHandler(sys.path[0]+'/info.log', encoding='utf8')
fh_info.setLevel(logging.INFO)


# 定义handler的输出格式
formatter = logging.Formatter(
    '%(asctime)s %(filename)s %(funcName)s [line:%(lineno)d] %(levelname)s %(message)s')
# 设置屏幕打印的格式
sh = logging.StreamHandler()
sh.setFormatter(formatter)
logger.addHandler(sh)
# 给handler添加formatter
fh_debug.setFormatter(formatter)
fh_info.setFormatter(formatter)

# 给logger添加handler
logger.addHandler(fh_debug)
logger.addHandler(fh_info)



# 发送邮件

""" 
content: 邮件内容
receivers: 接收者邮箱
ToName: 接收者名字
subject: 邮件主题
"""


def sendEmail(content, receivers, subject):
    if receivers == 'notSend':
        return
    if STMPConfig['enable'] == False:
        return
    yag = yagmail.SMTP(user={STMPConfig['Username']: STMPConfig['Sender']},
                       password=STMPConfig['Password'], host=STMPConfig['Host'], port=STMPConfig['Port'], smtp_ssl=True, encoding='utf-8')
    # 如果是管理员接收邮件，附带程序log
    if receivers == AdminEmail:
        # 读取文件info.log
        with open(sys.path[0]+'/info.log', 'r', encoding='UTF-8') as f:
            log = f.read()
        content += '\n\n\n\n'
        content += log

    # 发送邮件
    yag.send(
        # to 收件人，如果一个收件人用字符串，多个收件人用列表即可
        to=receivers,
        # subject 邮件主题（也称为标题）
        subject=subject,
        # contents 邮件正文
        contents=content,
    )
    yag.close()



# 打卡函数
""" 
Account: 学号
Password: 密码
Email: 要把打卡结果发送到哪个邮箱
"""


def report(Account, Password, Email):
    # 登录获取cookies
    headers = {
        'host': 'ehallapp.zwu.edu.cn:8080',
        'accept': 'application/json, text/plain, */*',
        'origin': 'https://ehallapp.zwu.edu.cn:8080',
        'referer': 'https://ehallapp.zwu.edu.cn:8080/app/login',
        'x-requested-with': 'XMLHttpRequest',
        'accept-language': 'zh-cn',
        'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_5_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
        'Connection': 'close',
    }

    json_data = {
        'PostBackType': 'LoginApp',
        'Data': {
            'Account': Account,
            'Password': Password,
            'AppVersion': '2.13',
        },
        'IsAppRequest': True,
    }

    response = requests.post(
        'https://ehallapp.zwu.edu.cn:8080/_layouts/15/ZWUWSBS/AppApi/System/AuthApi.aspx', headers=headers, json=json_data)

    # print(response.cookies)
    logger.debug(response.cookies)
    # print(response.text)
    # 检查response.text中是否包含'用户名或密码不正确'
    if '用户名或密码不正确' in response.text:
        print(Account+' 用户名或密码不正确')
        sendEmail('今日打卡失败\n请手动进行打卡\n原因：密码错误', Email,  '今日自动打卡失败，请注意！！！！')
        return

    ZWUCookies = response.cookies

    # 提取G2UserToken
    G2UserToken = str(ZWUCookies)[str(ZWUCookies).find(
        'G2UserToken=')+12:str(ZWUCookies).find(' for ehallapp.zwu.edu.cn/')]

    # 提取ZWU_KeepAutheticated
    ZWU_KeepAutheticated = str(ZWUCookies)[str(ZWUCookies).find('ZWU_KeepAutheticated=')+21:str(
        ZWUCookies).find(' for ehallapp.zwu.edu.cn/', str(ZWUCookies).find('ZWU_KeepAutheticated='))]
    # 暂停1s防止请求过快
    time.sleep(1)

    # 请求表单数据
    # 设置cookies
    account_cookies = {
        'G2UserToken': G2UserToken,
        'ZWU_KeepAutheticated': ZWU_KeepAutheticated,
        'loginstatus': '1',
    }

    getToDoFill_headers = {
        'host': 'ehallapp.zwu.edu.cn:8080',
        'accept': 'application/json, text/plain, */*',
        'x-requested-with': 'XMLHttpRequest',
        'accept-language': 'zh-cn',
        'origin': 'https://ehallapp.zwu.edu.cn:8080',
        'referer': 'https://ehallapp.zwu.edu.cn:8080/app/healthReport/dataFillingList',
        'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_5_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
        'Connection': 'close',
    }

    getToDoFill_json_data = {
        'PostBackType': 'getTodoFill',
        'IsAppRequest': True,
    }
    # 发送请求，获取今日要打卡的列表
    getToDoFill_response = requests.post('https://ehallapp.zwu.edu.cn:8080/_layouts/15/ZWUWSBS/AppApi/HealthReport/InformationQueryReportApi.aspx',
                                         cookies=account_cookies, headers=getToDoFill_headers, json=getToDoFill_json_data)

    # print("getToDoFill_response: " + getToDoFill_response.text)

    ToDoFill = json.loads(getToDoFill_response.text)
    if len(ToDoFill['Data']) == 0:
        logger.info(Account + ' 今日已填报')
        return
    else:
        logger.info(Account + ' 今日未填报，开始填报')

    # 提取json代码getToDoFill_ssresponse中的Id
    Id = getToDoFill_response.text[getToDoFill_response.text.find(
        '"Id":"')+6:getToDoFill_response.text.find('","SortAscending":false}')]
    logger.debug(Id)

    # 暂停1s防止请求过快
    time.sleep(1)

    getUserViewData_headers = {
        'host': 'ehallapp.zwu.edu.cn:8080',
        'accept': 'application/json, text/plain, */*',
        'x-requested-with': 'XMLHttpRequest',
        'accept-language': 'zh-cn',
        'origin': 'https://ehallapp.zwu.edu.cn:8080',
        'referer': 'https://ehallapp.zwu.edu.cn:8080/app/healthReport/dataFillingEditor?id='+Id+'&tabIndex=0',
        'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_5_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
        'Connection': 'close',
    }

    getUserViewData_json_data = {
        'PostBackType': 'getUserViewData',
        'Id': Id,
        'IsAppRequest': True,
    }
    # 发送请求，获取表单
    getUserViewData_response = requests.post('https://ehallapp.zwu.edu.cn:8080/_layouts/15/ZWUWSBS/AppApi/HealthReport/InformationReportApi.aspx',
                                             cookies=account_cookies, headers=getUserViewData_headers, json=getUserViewData_json_data)

    # 暂停1s防止请求过快
    time.sleep(1)

    reportForm = json.loads(getUserViewData_response.text)
    logger.debug(getUserViewData_response.text)

    if len(reportForm['Data']['InformationReportConentList']) != 5:
        logger.info('表单发生变化，请更新脚本。')
        sendEmail('表单发生变化，打卡失败，请手动打卡。', Email, '今日自动打卡失败，请注意！！！！！')
        return

    # 组合要发送的表单数据
    reportData = {}
    reportData['PostBackType'] = 'saveUserViewData'
    reportData['RequestObject'] = reportForm['Data']
    reportData['IsAppRequest'] = True

    post_headers = {
        'host': 'ehallapp.zwu.edu.cn:8080',
        'accept': 'application/json, text/plain, */*',
        'x-requested-with': 'XMLHttpRequest',
        'accept-language': 'zh-cn',
        'origin': 'https://ehallapp.zwu.edu.cn:8080',
        'referer': 'https://ehallapp.zwu.edu.cn:8080/app/healthReport/dataFillingEditor?id='+Id+'&tabIndex=0',
        'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_5_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
        'Connection': 'close',
    }

    post_response = requests.post('https://ehallapp.zwu.edu.cn:8080/_layouts/15/ZWUWSBS/AppApi/HealthReport/InformationReportApi.aspx',
                                  cookies=account_cookies, headers=post_headers, json=reportData)

    logger.debug(post_response.text)

    # 检查填报是否成功
    getToDoFill_response = requests.post('https://ehallapp.zwu.edu.cn:8080/_layouts/15/ZWUWSBS/AppApi/HealthReport/InformationQueryReportApi.aspx',
                                         cookies=account_cookies, headers=getToDoFill_headers, json=getToDoFill_json_data)

    ToDoFill = json.loads(getToDoFill_response.text)
    # 返回的json中的Data为空则填报成功
    global flag
    if len(ToDoFill['Data']) == 0:
        logger.info(Account + ' 填报成功')
        flag = flag + 1
        return
    else:
        logger.info(Account + ' 填报出现错误↓')
        logger.info("getToDoFill_response: " + getToDoFill_response.text)
        logger.debug(Account + ' 填报出现错误↓')
        logger.debug("getToDoFill_response: " + getToDoFill_response.text)
        sendEmail('今日打卡失败\n请手动进行打卡', Email, '今日自动打卡失败，请注意！！！！！')


if __name__ == '__main__':
    logger.info("开始运行")

    randomArr = []
    random.seed(time.time())
    randomList = []

    # 生成一个数组randomArr， 值为0-len(Account), 打卡随机顺序
    for i in range(len(Account)):
        randomArr.append(i)
    while len(randomArr):
        randomID = random.randint(0, len(randomArr)-1)
        randomList.append(randomArr[randomID])
        del randomArr[randomID]

    for i in randomList:
        # 生成1-1200的随机数(20分钟以内随机)，单位秒，可自行修改
        randomNum = random.randint(1, 10)
        logger.info(str(randomNum) + "秒后执行：" + Account[i]['Account'])
        time.sleep(randomNum)
        logger.info('正在填报第' + str(i+1) + '个账号')
        report(Account[i]['Account'], Account[i]['Password'],
               Account[i]['Email'])
        logger.info('第' + str(i+1) + '个账号填报完成')
        logger.info('')
    # 管理员打卡情况通知
    if flag == len(Account):
        sendEmail('今日打卡完成', AdminEmail, '今日自动打卡成功' + str(flag) + '个账号，共有' + str(len(Account)
                                                                                ) + '个账号')
    else:
        sendEmail('今天打卡出现错误', AdminEmail, '今日自动打卡成功' + str(flag) + '个账号，共有' + str(len(Account)
                                                                                  ) + '个账号')
    logger.info('完毕')
