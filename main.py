# -*- coding: utf-8 -*-
import json
import time
import requests
import random
import sys
import os
import yagmail
import logging
import uuid
import base64
import re
import datetime

# 记录成功打卡人数的标记
flag = 0


# 优先从当前目录下读取config.json文件，如果没有则从环境变量中读取
# 在当前目录下有config.json文件时，环境变量中的config变量将被忽略
try:
    with open(sys.path[0]+'/config.json', 'r',encoding='UTF-8') as f:
        jsonObj = json.loads(f.read())
        Account = jsonObj['account']
        STMPConfig = jsonObj['STMP']
        AdminEmail = jsonObj['AdminEmail']
except FileNotFoundError:
    conf = os.getenv('config')
    Account = (json.loads(conf))['account']
    STMPConfig = (json.loads(conf))['STMP']
    AdminEmail = (json.loads(conf))['AdminEmail']


# 位置信息
# 在浙江万里学院宿舍楼26号楼，39号楼，28号楼，43号楼，文韵楼，22号楼，41号楼，方圆100米内生成随机位置
randomLocation = ['浙江万里学院宿舍楼-26号楼北102米', '浙江万里学院宿舍楼-39号楼北101米', '浙江万里学院宿舍楼-28号楼北310米', '浙江万里学院宿舍楼-43号楼北120米', '浙江万里学院宿舍楼-文韵楼北310米', '浙江万里学院宿舍楼-22号楼北120米', '浙江万里学院宿舍楼-41号楼北130米', '浙江万里学院宿舍楼-26号楼北102米', '浙江万里学院宿舍楼-39号楼北101米', '浙江万里学院宿舍楼-28号楼北210米', '浙江万里学院宿舍楼-43号楼北320米', '浙江万里学院宿舍楼-文韵楼北30米', '浙江万里学院宿舍楼-22号楼北20米', '浙江万里学院宿舍楼-41号楼北230米',
                  '浙江万里学院宿舍楼-26号楼北12米', '浙江万里学院宿舍楼-39号楼北10米', '浙江万里学院宿舍楼-28号楼北10米', '浙江万里学院宿舍楼-43号楼北11米', '浙江万里学院宿舍楼-文韵楼北16米', '浙江万里学院宿舍楼-22号楼北50米', '浙江万里学院宿舍楼-41号楼北21米', '浙江万里学院宿舍楼-26号楼北153米', '浙江万里学院宿舍楼-39号楼北105米', '浙江万里学院宿舍楼-28号楼北26米', '浙江万里学院宿舍楼-43号楼北150米', '浙江万里学院宿舍楼-文韵楼北313米', '浙江万里学院宿舍楼-22号楼北220米', '浙江万里学院宿舍楼-41号楼北130米']
CurrentLocation = '浙江省宁波市鄞州区首南街道 浙江万里学院(钱湖校区)内, '
# 程序会在经纬度两个值之后插入一个五位的随机数，来保证每次提交的经纬度都不是一样的
LatitudeLongitude = '29.822667977,121.566843999'
Province = '浙江省'
City = '宁波市'
District = '鄞州区'
Address = '浙江省宁波市鄞州区钱湖街道万里学院(钱湖校区)'
Street = '首南街道'
# 请自行修改以上信息

# 配置输出log信息
logger = logging.getLogger()
logger.setLevel(logging.INFO)   # 设置打印级别
formatter = logging.Formatter(
    '%(asctime)s %(filename)s %(funcName)s [line:%(lineno)d] %(levelname)s %(message)s')
# 设置屏幕打印的格式
sh = logging.StreamHandler()
sh.setFormatter(formatter)
logger.addHandler(sh)
# 设置log保存
fh = logging.FileHandler("info.log", encoding='utf8')
fh.setFormatter(formatter)
logger.addHandler(fh)

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
        with open(sys.path[0]+'/info.log', 'r',encoding='UTF-8') as f:
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


def getYesterdayImage(G2UserToken, ZWU_KeepAutheticated, FormNumber):
    print('获取昨日图片')

    # 获取打卡记录列表
    getYesterdayImage_cookies = {
        'G2UserToken': G2UserToken,
        'ZWU_KeepAutheticated': ZWU_KeepAutheticated,
        'loginstatus': '1',
    }

    getYesterdayImage_headers = {
        'host': 'ehallapp.zwu.edu.cn:8080',
        'accept': 'application/json, text/plain, */*',
        'x-requested-with': 'XMLHttpRequest',
        'accept-language': 'zh-cn',
        'origin': 'https://ehallapp.zwu.edu.cn:8080',
        'referer': 'https://ehallapp.zwu.edu.cn:8080/app/healthReport/dataFillingList',
        'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_5_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
        'Connection': 'close',
    }

    getYesterdayImage_json_data = {
        'PostBackType': 'getDoneFillUserList',
        'InfoId': '',
        'ActionCode': 'InfoReport_list',
        'PunchStatus': '1',
        'loadingMessage': '加载中...',
        'IsAppRequest': True,
    }

    getYesterdayImage_response = requests.post('https://ehallapp.zwu.edu.cn:8080/_layouts/15/ZWUWSBS/AppApi/HealthReport/InformationQueryReportApi.aspx',
                                               cookies=getYesterdayImage_cookies, headers=getYesterdayImage_headers, json=getYesterdayImage_json_data)

    # print(response.text)
    dailyLIst = json.loads(getYesterdayImage_response.text)
    # 获取昨日日期，格式为10-28
    yesterdayDate = (datetime.datetime.now() +
                     datetime.timedelta(days=-1)).strftime("%m-%d")
    logging.info(yesterdayDate)

    # 找到昨日打卡记录
    # 可能存在的bug：如果昨天没打卡，获取图片将会失败，不会自动前推一天
    for i in dailyLIst['Data']:
        if yesterdayDate in i['Created']:
            RegistrationId = i['Id']
            InfoId = i['InfoId']

    logging.info(RegistrationId)
    logging.info(InfoId)

    # 获取昨天的表单
    yesterday_headers = {
        'host': 'ehallapp.zwu.edu.cn:8080',
        'accept': 'application/json, text/plain, */*',
        'x-requested-with': 'XMLHttpRequest',
        'accept-language': 'zh-cn',
        'origin': 'https://ehallapp.zwu.edu.cn:8080',
        'referer': 'https://ehallapp.zwu.edu.cn:8080/app/healthReport/dataFillingEditor?id='+InfoId+'&registrationId='+RegistrationId,
        'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_5_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
        'Connection': 'close',
    }

    yesterday_json_data = {
        'PostBackType': 'getUserViewData',
        'RegistrationId': RegistrationId,
        'Id': InfoId,
        'IsAppRequest': True,
    }

    yesterday_response = requests.post('https://ehallapp.zwu.edu.cn:8080/_layouts/15/ZWUWSBS/AppApi/HealthReport/InformationReportApi.aspx',
                                       cookies=getYesterdayImage_cookies, headers=yesterday_headers, json=yesterday_json_data)

    # 处理昨天的表单，提取图片
    # print(response.text)
    yesterday_data = json.loads(yesterday_response.text)
    yesterday_url = yesterday_data['Data']['InformationReportConentList'][FormNumber]['AttachmentDataList'][0]['Url']

    # 提取cid和uid
    cid = re.findall(r'cid=(.*?)&', yesterday_url)[0]
    uid = re.findall(r'uid=(.*?)$', yesterday_url)[0]
    logging.info(cid)
    logging.info(uid)

    # 获取图片

    image_headers = {
        'host': 'ehallapp.zwu.edu.cn:8080',
        # Requests sorts cookies= alphabetically
        'accept': 'image/png,image/svg+xml,image/*;q=0.8,video/*;q=0.8,*/*;q=0.5',
        'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_5_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
        'accept-language': 'zh-cn',
        'referer': 'https://ehallapp.zwu.edu.cn:8080/app/healthReport/dataFillingEditor?id='+InfoId+'&registrationId='+RegistrationId,
        'Connection': 'close',
    }

    params = {
        'cid': cid,
        'uid': uid,
    }

    image_response = requests.get('https://ehallapp.zwu.edu.cn:8080/_layouts/15/ZWUWSBS/AppApi/HealthReport/InformationReportApi.aspx',
                                  params=params, cookies=getYesterdayImage_cookies, headers=image_headers)

    # 把image_response中的图片转换成base64文本编码，并返回
    image_base64 = base64.b64encode(image_response.content)
    return image_base64.decode()


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
        # Already added when you pass json=
        # 'content-type': 'application/json',
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
    logging.info(response.cookies)
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
        # Already added when you pass json=
        # 'content-type': 'application/json',
        'accept': 'application/json, text/plain, */*',
        'x-requested-with': 'XMLHttpRequest',
        'accept-language': 'zh-cn',
        'origin': 'https://ehallapp.zwu.edu.cn:8080',
        'referer': 'https://ehallapp.zwu.edu.cn:8080/app/healthReport/dataFillingList',
        'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_5_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
        # Requests sorts cookies= alphabetically
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
        logging.info(Account + ' 今日已填报')
        return
    else:
        logging.info(Account + ' 今日未填报，开始填报')

    # 提取json代码getToDoFill_ssresponse中的Id
    Id = getToDoFill_response.text[getToDoFill_response.text.find(
        '"Id":"')+6:getToDoFill_response.text.find('","SortAscending":false}')]
    logging.info(Id)

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

    # 将位置信息添加到表单中
    reportForm = json.loads(getUserViewData_response.text)
    logging.info(getUserViewData_response.text)

    reportForm['Data']['InformationReportConentList'][
        1]['QuestionAnswer'] = CurrentLocation + randomLocation[random.randint(0, len(randomLocation) - 1)]

    # 生成随机数使得每次的LatitudeLongitude都不相同
    random_num1 = random.randint(10000, 99999)
    random_num2 = random.randint(10000, 99999)
    reportForm['Data']['InformationReportConentList'][1]['LatitudeLongitude'] = LatitudeLongitude[:LatitudeLongitude.find(
        ',')] + str(random_num1) + LatitudeLongitude[LatitudeLongitude.find(','):] + str(random_num2)
    reportForm['Data']['InformationReportConentList'][1]['Province'] = Province
    reportForm['Data']['InformationReportConentList'][1]['City'] = City
    reportForm['Data']['InformationReportConentList'][1]['Area'] = District
    reportForm['Data']['InformationReportConentList'][1]['Street'] = Street
    reportForm['Data']['InformationReportConentList'][1][
        'StrDetailAddresseet'] = CurrentLocation
    # 你申请的支付宝健康码是
    reportForm['Data']['InformationReportConentList'][3]['QuestionAnswer'] = 'A'

    # 获取今天的日期的天数
    today = datetime.date.today().day
    # 如果today是10的倍数，24小时内是否做过核酸=A
    if today % 10 == 0:
        reportForm['Data']['InformationReportConentList'][8]['QuestionAnswer'] = 'A'
    else:
        reportForm['Data']['InformationReportConentList'][8]['QuestionAnswer'] = 'B'

    # 将获取截图信息改写为循环
    screenshotNum = 0
    for items in [4]:
        screenshotNum = screenshotNum+1
        picIsExist = False
        try:
            # 件康马在数组4的位置
            pic_64 = getYesterdayImage(
                G2UserToken, ZWU_KeepAutheticated, items)
            logging.info('获取昨日件康马成功')
            picIsExist = True
        except Exception as es:
            logging.error('获取昨日件康马失败')
            logging.error(es)
            try:
                pic = open(sys.path[0]+'/screenshot' +
                           screenshotNum+'/'+Account + '.jpeg', 'rb')
                pic_read = pic.read()
                pic_64 = base64.b64encode(pic_read)
                pic_64 = pic_64.decode()
                # 星橙卡备用
                logging.info("图片读取成功")
                picIsExist = True
            except Exception as e:
                logging.info("图片读取失败, 不上传件康马图片")
                picIsExist = False
                logging.error(e)
        # 如果图片存在并读取成功，将图片添加到表单中
        if picIsExist:
            # 件康马
            AttachmentDataList = []
            picInfo = {
                'Data': 'data:image/jpeg;base64,' + pic_64,
                'FileName': (str(uuid.uuid4())).upper()+'.jpeg',
                'ModiState': 'C',
                'UniqueId': str((uuid.uuid4()).hex)
            }
            AttachmentDataList.append(picInfo)
            reportForm['Data']['InformationReportConentList'][items]['AttachmentDataList'] = AttachmentDataList

    if len(reportForm['Data']['InformationReportConentList']) != 9:
        logging.info('表单发生变化，请更新脚本。')
        sendEmail('表单发生变化，打卡失败，请手动打卡。', Email, '今日自动打卡失败，请注意！！！！！')
        return

    # 组合要发送的表单数据
    reportData = {}
    reportData['PostBackType'] = 'saveUserViewData'
    reportData['RequestObject'] = reportForm['Data']
    reportData['IsAppRequest'] = True

    post_headers = {
        'host': 'ehallapp.zwu.edu.cn:8080',
        # Already added when you pass json=
        # 'content-type': 'application/json',
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

    logging.info(post_response.text)

    # 检查填报是否成功
    getToDoFill_response = requests.post('https://ehallapp.zwu.edu.cn:8080/_layouts/15/ZWUWSBS/AppApi/HealthReport/InformationQueryReportApi.aspx',
                                         cookies=account_cookies, headers=getToDoFill_headers, json=getToDoFill_json_data)

    ToDoFill = json.loads(getToDoFill_response.text)
    # 返回的json中的Data为空则填报成功
    global flag
    if len(ToDoFill['Data']) == 0:
        logging.info(Account + ' 填报成功')
        flag = flag + 1
        return
    else:
        logging.info(Account + ' 填报出现错误↓')
        logging.info("getToDoFill_response: " + getToDoFill_response.text)
        sendEmail('今日打卡失败\n请手动进行打卡', Email, '今日自动打卡失败，请注意！！！！！')


logging.info("开始运行")

randomArr = []
random.seed(time.time())
randomList=[]

# 生成一个数组randomArr， 值为0-len(Account), 打卡随机顺序
for i in range(len(Account)):
    randomArr.append(i)
while len(randomArr):
    randomID=random.randint(0, len(randomArr)-1)
    randomList.append(randomArr[randomID])
    del randomArr[randomID]

for i in randomList:
    # 生成1-1200的随机数(20分钟以内随机)，单位秒，可自行修改
    randomNum = random.randint(1, 1200)
    logging.info(str(randomNum) + "秒后执行：" + Account[i]['Account'])
    time.sleep(randomNum)
    logging.info('正在填报第' + str(i+1) + '个账号')
    report(Account[i]['Account'], Account[i]['Password'],
           Account[i]['Email'])
    logging.info('第' + str(i+1) + '个账号填报完成')
    logging.info('')
# 管理员打卡情况通知
if flag == len(Account):
    sendEmail('今日打卡完成', AdminEmail, '今日自动打卡成功' + str(flag) + '个账号，共有' + str(len(Account)
                                                                            ) + '个账号')
else:
    sendEmail('今天打卡出现错误', AdminEmail, '今日自动打卡成功' + str(flag) + '个账号，共有' + str(len(Account)
                                                                              ) + '个账号')
logging.info('完毕')
