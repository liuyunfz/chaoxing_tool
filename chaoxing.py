#!/usr/bin/env python
# _*_ coding:utf-8 _*_
import json
import re
import threading
from queue import Queue
from urllib import parse

import base64
import os
import requests
import sys
import time
from lxml import etree

global video_url_list
video_url_list = []


# 视频任务enc校验计算
def encode_enc(clazzid: str, duration: int, objectId: str, otherinfo: str, jobid: str, userid: str, currentTimeSec: str):
    import hashlib
    data = "[{0}][{1}][{2}][{3}][{4}][{5}][{6}][0_{7}]".format(clazzid, userid, jobid, objectId, int(currentTimeSec) * 1000, "d_yHJ!$pdA~5", duration * 1000, duration)
    print(data)
    return hashlib.md5(data.encode()).hexdigest()


# 手机号登录，返回response
def sign_in(uname: str, password: str):
    sign_in_url = "https://passport2.chaoxing.com/fanyalogin"
    sign_in_data = "fid=314&uname={0}&password={1}&refer=http%253A%252F%252Fi.mooc.chaoxing.com&t=true".format(uname, base64.b64encode(password.encode("utf-8")).decode("utf-8"))
    sign_in_headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Connection': 'keep-alive',
        'Content-Length': '98',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Cookie': 'route=3744838b34ea6b4834cd438e19ed44f0; JSESSIONID=9CD969F9C1B9633A46EAD7880736DD51; fanyamoocs=11401F839C536D9E; fid=314; isfyportal=1; ptrmooc=t',
        'Host': 'passport2.chaoxing.com',
        'Origin': 'https://passport2.chaoxing.com',
        'Referer': 'https://passport2.chaoxing.com/login?loginType=4&fid=314&newversion=true&refer=http://i.mooc.chaoxing.com',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36 Edg/85.0.564.51',
        'X-Requested-With': 'XMLHttpRequest'
    }
    sign_in_rsp = requests.post(url=sign_in_url, data=sign_in_data, headers=sign_in_headers)
    return sign_in_rsp


# 任务1：用户登录，并合并cookie
def step_1():
    sign_sus = False
    while sign_sus == False:
        os.system("cls")
        uname = input("请输入您的手机号:")
        import getpass
        password = getpass.getpass("请输入您的密码:")
        sign_in_rsp = sign_in(uname, password)
        sign_in_json = sign_in_rsp.json()
        if sign_in_json['status'] == False:
            print(sign_in_json.get('msg2'), "\n\n请按回车重新键入账号数据")
            input()
        else:
            sign_sus = True
            print("登陆成功，正在处理您的数据...")
    global cookieStr, uid, global_headers
    uid = sign_in_rsp.cookies['_uid']
    cookieStr = ''
    for item in sign_in_rsp.cookies:
        cookieStr = cookieStr + item.name + '=' + item.value + ';'
    global_headers = {
        'Cookie': cookieStr,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36 Edg/85.0.564.51'
    }


# 任务2：课程读取，并输出课程信息
def step_2():
    class_url = "http://mooc1-2.chaoxing.com/visit/courses"
    class_rsp = requests.get(url=class_url, headers=global_headers)
    if class_rsp.status_code == 200:
        class_HTML = etree.HTML(class_rsp.text)
        os.system("cls")
        print("处理成功，您当前已开启的课程如下：\n")
        i = 0
        global course_dict
        course_dict = {}
        for class_item in class_HTML.xpath("/html/body/div/div[2]/div[3]/ul/li[@class='courseItem curFile']"):
            try:
                class_item_name = class_item.xpath("./div[2]/h3/a/@title")[0]
                # 等待开课的课程由于尚未对应链接，所以缺少a标签。
                i += 1
                print(class_item_name)
                course_dict[i] = [class_item_name, "https://mooc1-2.chaoxing.com{}".format(class_item.xpath("./div[1]/a[1]/@href")[0])]
            except:
                pass
        print("———————————————————————————————————")
    else:
        print("课程处理失败，请联系作者")
    # print(course_dict)


# 获取url重定向后的新地址与cpi
def url_302(oldUrl: str):
    # 302跳转，requests库默认追踪headers里的location进行跳转，使用allow_redirects=False
    course_302_rsp = requests.get(url=oldUrl, headers=global_headers, allow_redirects=False)
    new_url = course_302_rsp.headers['Location']
    result = parse.urlparse(new_url)
    new_url_data = parse.parse_qs(result.query)
    try:
        cpi = new_url_data.get("cpi")[0]
    except:
        print("fail to get cpi")
        cpi = None
    return {"new_url": new_url, "cpi": cpi}


# 获取所有课程信息
def course_get(url: str):
    course_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Connection': 'keep-alive',
        'Cookie': cookieStr,
        'Host': 'mooc1-2.chaoxing.com',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36 Edg/85.0.564.51'
    }
    course_rsp = requests.get(url=url, headers=course_headers)
    course_HTML = etree.HTML(course_rsp.text)
    return course_HTML


# 递归读取章节
def recursive_course(course_unit_list, chapter_mission, level):
    for course_unit in course_unit_list:
        h3_list = course_unit.xpath("./h3")
        for h3_item in h3_list:
            chapter_status = __list_get(h3_item.xpath("./a/span[@class='icon']/em/@class"))
            if chapter_status == "orange":
                print("--" * level, __list_get(h3_item.xpath("./a/span[@class='articlename']/@title")), "      ", __list_get(h3_item.xpath("./a/span[@class='icon']/em/text()")))
                chapter_mission.append("https://mooc1-2.chaoxing.com{}".format(__list_get(h3_item.xpath("./a/@href"))))
            else:
                print("--" * level, __list_get(h3_item.xpath("./a/span[@class='articlename']/@title")), "      ", chapter_status)
        chapter_item_list = course_unit.xpath("./div")
        if chapter_item_list:
            recursive_course(chapter_item_list, chapter_mission, level + 1)


# thread
def createQueue(urls):
    urlQueue = Queue()
    for url in urls:
        urlQueue.put(url)
    return urlQueue


class spiderThread(threading.Thread):
    def __init__(self, threadName, urlQueue, cpi):
        super(spiderThread, self).__init__()
        self.threadName = threadName
        self.urlQueue = urlQueue
        self.cpi = cpi

    def run(self):
        while True:
            if self.urlQueue.empty():
                break
            chapter = self.urlQueue.get()
            deal_misson([chapter], self.cpi, 0)
            time.sleep(0.2)


def createThread(threadCount, urlQueue, cpi):
    threadQueue = []
    for i in range(threadCount):
        spiderThreading = spiderThread("threading_{}".format(i), urlQueue=urlQueue, cpi=cpi)  # 循环创建多个线程，并将队列传入
        threadQueue.append(spiderThreading)  # 将线程放入线程池
    return threadQueue


# 选取有任务点的课程,并处理
def deal_course_select(url_class):
    new_url_dict = url_302(url_class)
    new_url = new_url_dict["new_url"]
    course_HTML = course_get(new_url)
    # 为防止账号没有课程或没有班级，需要后期在xpath获取加入try，以防报错
    chapter_mission = []
    try:
        course_unit_list = course_HTML.xpath("//div[@class='units']")
        for course_unit in course_unit_list:
            print(__list_get(course_unit.xpath("./h2/a/@title")))
            recursive_course(course_unit.xpath("./div"), chapter_mission, 1)
    except Exception as e:
        print("deal_course_select error %s" % e)

    print("课程读取完成，共有%d个章节可一键完成" % len(chapter_mission))
    # if len(chapter_mission) > 20:
    #     print("章节数大于20，已为您自动启动多线程")
    #     threadQueue = createThread(6, createQueue(chapter_mission), new_url_dict["cpi"])
    #     for thread in threadQueue:
    #         thread.start()  # 线程池启动
    #     for thread in threadQueue:
    #         thread.join()  # 线程池销毁
    # else:
    deal_misson(chapter_mission, new_url_dict["cpi"], 0)


# 递归读取所有课程信息，返回dict
def recursive_course_dict(course_unit_list, chapter_dict):
    for course_unit in course_unit_list:
        h3_list = course_unit.xpath("./h3")
        for h3_item in h3_list:
            chapter_dict.update({__list_get(h3_item.xpath("./a/span[@class='chapterNumber']/text()")) + __list_get(h3_item.xpath("./a/span[@class='articlename']/span[@class='chapterNumber']/text()")) + __list_get(h3_item.xpath("./a/span[@class='articlename']/@title")): __list_get(h3_item.xpath("./a/@href"))})
        chapter_item_list = course_unit.xpath("./div")
        if chapter_item_list:
            recursive_course_dict(chapter_item_list, chapter_dict)


# 获取所有的课程信息，并储存url
def deal_course_all(url_class):
    new_url_dict = url_302(url_class)
    new_url = new_url_dict["new_url"]
    course_HTML = course_get(new_url)
    i = 0
    chapter_dict = {}
    course_unit_list = course_HTML.xpath("//div[@class='units']")  # 课程中的大章节
    try:
        for course_unit in course_unit_list:
            recursive_course_dict(course_unit.xpath("./div"), chapter_dict)
        chapter_list = []
        for chapter_item in chapter_dict:
            i = i + 1
            try:
                print("%d" % i, chapter_item)
                chapter_list.append(chapter_dict[chapter_item])
            except Exception as e:
                print("chapter处理错误", e)
    except Exception as e:
        print(e)
    while True:
        enter = input("请输入资源所在章节的序号：")
        try:
            url_chapter = chapter_list[int(enter) - 1]
            deal_misson([url_chapter], new_url_dict["cpi"], 1)
            break
        except Exception as e:
            print("'%s'不是可识别的输入，请重新输入" % enter)


# 读取章节页数
def read_cardcount(courseId: str, clazzid: str, chapterId: str, cpi: str):
    url = 'https://mooc1-2.chaoxing.com/mycourse/studentstudyAjax'
    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Connection': 'keep-alive',
        'Content-Length': '87',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Cookie': cookieStr,
        'Host': 'mooc1-2.chaoxing.com',
        'Origin': 'https://mooc1-2.chaoxing.com',
        'Referer': 'https://mooc1-2.chaoxing.com/mycourse/studentstudy?chapterId=357838590&courseId=214734258&clazzid=32360675&enc=ccf66103f539dfec439e4898b62c8024',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36 Edg/87.0.664.60',
        'X-Requested-With': 'XMLHttpRequest'
    }
    data = "courseId={0}&clazzid={1}&chapterId={2}&cpi={3}&verificationcode=".format(courseId, clazzid, chapterId, cpi)
    rsp = requests.post(url=url, headers=headers, data=data)
    rsp_HTML = etree.HTML(rsp.text)
    return rsp_HTML.xpath("//input[@id='cardcount']/@value")[0]


# 处理video任务,校验为enc
def misson_video(objectId, otherInfo, jobid, name, reportUrl, clazzId):
    status_url = "https://mooc1-1.chaoxing.com/ananas/status/{}?k=&flag=normal&_dc=1600850935908".format(objectId)
    status_rsp = requests.get(url=status_url, headers=global_headers)
    status_json = json.loads(status_rsp.text)
    duration = status_json.get('duration')
    dtoken = status_json.get('dtoken')
    print(objectId, otherInfo, jobid, uid, name, duration, reportUrl)
    # multimedia_headers = {
    #     'Accept': '*/*',
    #     'Accept-Encoding': 'gzip, deflate, br',
    #     'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    #     'Connection': 'keep-alive',
    #     'Content-Type': 'application/json',
    #     'Cookie': cookieStr,
    #     'Host': 'mooc1-1.chaoxing.com',
    #     'Referer': 'https://mooc1-1.chaoxing.com/ananas/modules/video/index.html?v=2020-0907-1546',
    #     'Sec-Fetch-Dest': 'empty',
    #     'Sec-Fetch-Mode': 'cors',
    #     'Sec-Fetch-Site': 'same-origin',
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36 Edg/85.0.564.51'
    # }

    elses = "/{0}?clazzId={1}&playingTime={2}&duration={2}&clipTime=0_{2}&objectId={3}&otherInfo={4}&jobid={5}&userid={6}&isdrag=0&view=pc&enc={7}&rt=0.9&dtype=Video&_t={8}".format(dtoken, clazzId, duration, objectId, otherInfo, jobid, uid, encode_enc(clazzId, duration, objectId, otherInfo, jobid, uid, duration), int(time.time() * 1000))
    reportUrl_item = reportUrl + str(elses)
    video_url_list.append(reportUrl_item)
    # multimedia_rsp = requests.get(url=reportUrl_item, headers=multimedia_headers)
    print("检测到一个视频节点，已添加到任务列表")
    return reportUrl_item


# 处理live任务，核心为获取视频token
def misson_live(streamName, jobid, vdoid, courseId, chapterId, clazzid):
    src = 'https://live.chaoxing.com/courseLive/newpclive?streamName=' + streamName + '&vdoid=' + vdoid + '&width=630&height=530' + '&jobid=' + jobid + '&userId={0}&knowledgeid={1}&ut=s&clazzid={2}&courseid={3}'.format(uid, chapterId, clazzid, courseId)
    rsp = requests.get(url=src, headers=global_headers)
    rsp_HTML = etree.HTML(rsp.text)
    token_url = rsp_HTML.xpath("//iframe/@src")[0]
    print(token_url)
    token_result = parse.urlparse(token_url)
    token_data = parse.parse_qs(token_result.query)
    token = token_data.get("token")
    finish_url = "https://zhibo.chaoxing.com/live/saveCourseJob?courseId={0}&knowledgeId={1}&classId={2}&userId={3}&jobId={4}&token={5}".format(courseId, chapterId, clazzid, uid, jobid, token[0])
    finish_rsp = requests.get(url=finish_url, headers=global_headers)
    print(finish_rsp.text)


# 处理document任务，核心为jtoken
def misson_doucument(jobid, chapterId, courseid, clazzid, jtoken):
    multimedia_headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Connection': 'keep-alive',
        'Cookie': cookieStr,
        'Host': 'mooc1-2.chaoxing.com',
        'Referer': 'https://mooc1-2.chaoxing.com/ananas/modules/pdf/index.html?v=2020-1103-1706',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36 Edg/87.0.664.52',
        'X-Requested-With': 'XMLHttpRequest'
    }
    url = 'https://mooc1-2.chaoxing.com/ananas/job/document?jobid={0}&knowledgeid={1}&courseid={2}&clazzid={3}&jtoken={4}&_dc=1607066762782'.format(jobid, chapterId, courseid, clazzid, jtoken)
    multimedia_rsp = requests.get(url=url, headers=multimedia_headers)
    print(multimedia_rsp.text)


# 处理book任务，核心为jtoken
def misson_book(jobid, chapterId, courseid, clazzid, jtoken):
    multimedia_headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Connection': 'keep-alive',
        'Cookie': cookieStr,
        'Host': 'mooc1-2.chaoxing.com',
        'Referer': 'https://mooc1-2.chaoxing.com/ananas/modules/innerbook/index.html?v=2018-0126-1905',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36 Edg/87.0.664.52',
        'X-Requested-With': 'XMLHttpRequest'
    }
    url = 'https://mooc1-2.chaoxing.com/ananas/job?jobid={0}&knowledgeid={1}&courseid={2}&clazzid={3}&jtoken={4}&_dc={5}'.format(jobid, chapterId, courseid, clazzid, jtoken, int(time.time() * 1000))
    multimedia_rsp = requests.get(url=url, headers=multimedia_headers)
    print(multimedia_rsp.text)


# 处理read任务，核心为jtoken
def misson_reed(jobid, chapterId, courseid, clazzid, jtoken):
    multimedia_headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Connection': 'keep-alive',
        'Cookie': cookieStr,
        'Host': 'mooc1-2.chaoxing.com',
        'Referer': 'https://mooc1-2.chaoxing.com/ananas/modules/innerbook/index.html?v=2018-0126-1905',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36 Edg/87.0.664.52',
        'X-Requested-With': 'XMLHttpRequest'
    }
    url = 'https://mooc1-2.chaoxing.com/ananas/job/readv2?jobid={0}&knowledgeid={1}&courseid={2}&clazzid={3}&jtoken={4}&_dc={5}'.format(jobid, chapterId, courseid, clazzid, jtoken, int(time.time() * 1000))
    multimedia_rsp = requests.get(url=url, headers=multimedia_headers)
    print(multimedia_rsp.text)


# 课程学习次数
def set_log(course_url: str):
    course_rsp = requests.get(url=url_302(course_url)["new_url"], headers=global_headers)
    course_HTML = etree.HTML(course_rsp.text)
    log_url = course_HTML.xpath("/html/body/script[11]/@src")[0]
    rsp = requests.get(url=log_url, headers=global_headers)
    print(rsp.text)


# 处理任务
def deal_misson(missons: list, class_cpi: str, mode: int):
    for chapter_mission_item in missons:
        result = parse.urlparse(chapter_mission_item)
        chapter_data = parse.parse_qs(result.query)
        clazzId = chapter_data.get('clazzid')[0]
        courseId = chapter_data.get('courseId')[0]
        chapterId = chapter_data.get('chapterId')[0]
        cardcount = int(read_cardcount(courseId, clazzId, chapterId, class_cpi))
        for num in range(cardcount):
            print("num:", num)
            medias_url = "https://mooc1-2.chaoxing.com/knowledge/cards?clazzid={0}&courseid={1}&knowledgeid={2}&num={4}&ut=s&cpi={3}&v=20160407-1".format(clazzId, courseId, chapterId, class_cpi, num)
            medias_rsp = requests.get(url=medias_url, headers=global_headers)
            medias_HTML = etree.HTML(medias_rsp.text)
            medias_text = medias_HTML.xpath("//script[1]/text()")[0]
            pattern = re.compile(r"mArg = ({[\s\S]*)}catch")
            datas = re.findall(pattern, medias_text)[0]
            datas = json.loads(datas.strip()[:-1])
            if mode == 0:
                # mode 0 deal misson
                medias_deal(datas, clazzId, chapterId, courseId, chapter_mission_item)
            else:
                # mode 1 download medias
                medias_download(datas["attachments"])


# 判断媒体类型并处理
def medias_deal(data, clazzId, chapterId, courseId, chapterUrl):
    result_json = data["attachments"]
    for media_item in result_json:
        if media_item.get("job") == None:
            continue
        media_type = media_item.get("type")
        jobid = media_item.get("jobid")
        if media_type == "video":
            objectId = media_item.get("objectId")
            otherInfo = media_item.get("otherInfo")
            name = media_item.get('property').get('name')
            url_video = misson_video(objectId=objectId, otherInfo=otherInfo, jobid=jobid, name=name, reportUrl=data["defaults"]["reportUrl"], clazzId=clazzId)
            # multimedia_headers = {
            #     'Accept': '*/*',
            #     'Accept-Encoding': 'gzip, deflate, br',
            #     'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            #     'Connection': 'keep-alive',
            #     'Content-Type': 'application/json',
            #     'Cookie': cookieStr,
            #     'Host': 'mooc1-1.chaoxing.com',
            #     'Referer': 'https://mooc1-1.chaoxing.com/ananas/modules/video/index.html?v=2020-0907-1546',
            #     'Sec-Fetch-Dest': 'empty',
            #     'Sec-Fetch-Mode': 'cors',
            #     'Sec-Fetch-Site': 'same-origin',
            #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36 Edg/85.0.564.51'
            # }
            # rsp = requests.get(url=url_video, headers=multimedia_headers)
            # print(rsp.text)
        elif media_type == "live":
            streamName = media_item.get("property").get("streamName")
            vdoid = media_item.get("property").get("vdoid")
            misson_live(streamName, jobid, vdoid, courseId, chapterId, clazzId)
        elif media_type == "document":
            jtoken = media_item.get("jtoken")
            misson_doucument(jobid, chapterId, courseId, clazzId, jtoken)
        elif "bookname" in media_item["property"]:
            jtoken = media_item.get("jtoken")
            misson_book(jobid, chapterId, courseId, clazzId, jtoken)
        elif media_type == "read":
            jtoken = media_item.get("jtoken")
            misson_read(jobid, chapterId, courseId, clazzId, jtoken)


# 下载媒体
def medias_download(medias):
    downloads_dict = {}
    i = 0
    for media_item in medias:
        objectid = media_item.get("property").get("objectid")
        if objectid == None:
            continue
        status_rsp = requests.get(url="https://mooc1-1.chaoxing.com/ananas/status/{}?k=&flag=normal&_dc=1600850935908".format(objectid), headers=global_headers)
        status_json = json.loads(status_rsp.text)
        filename = status_json.get('filename')
        if status_json.get("pagenum") != None:
            download = status_json.get('pdf')
        else:
            download = status_json.get('http')
        i += 1
        downloads_dict[i] = [filename, download]
        print(i, ".       ", filename)
    if downloads_dict == {}:
        print("所在章节无可下载的资源")
        return False
    enter = input("请输入你要下载资源的序号，以逗号分隔：")
    enter_list = enter.split(",")
    download_headers = global_headers
    download_headers.update({
        "referer": "https://mooc1-2.chaoxing.com/ananas/modules/video/index.html?v=2021-0924-1446",
        "Host": "s1.ananas.chaoxing.com"
    })
    for media_index in enter_list:
        try:
            with open(downloads_dict[int(media_index)][0], "wb") as f:
                print("\n正在下载%s..." % downloads_dict[int(media_index)][0])
                rsp = requests.get(url=downloads_dict[int(media_index)][1], headers=download_headers, stream=True)
                length_already = 0
                length_all = int(rsp.headers['content-length'])
                for chunk in rsp.iter_content(chunk_size=5242880):
                    if chunk:
                        length_already += len(chunk)
                        print("\r下载进度：%d%%" % int(length_already / length_all * 100), end="", flush=True)
                        f.write(chunk)
                print("\n下载完成,其中PPT请手动修改后缀为PDF打开")
                f.close()
        except OSError:
            new_name = str(int(time.time())) + os.path.splitext(downloads_dict[int(media_index)][0])[-1]
            print("由于windows不允许文件包含特殊字符，已将文件重命名为 %s" % new_name)
            with open(new_name, "wb") as f:
                print("\n正在下载%s..." % new_name)
                length_already = 0
                length_all = int(rsp.headers['content-length'])
                for chunk in rsp.iter_content(chunk_size=5242880):
                    if chunk:
                        length_already += len(chunk)
                        print("\r下载进度：%d%%" % int(length_already / length_all * 100), end="", flush=True)
                        f.write(chunk)
                print("\n下载完成")
                f.close()
        except Exception as e:
            print("文件下载错误：", e)


def __list_get(list: list):
    if len(list):
        return list[0]
    else:
        return ""


class VideoThread(threading.Thread):
    def __init__(self, post_url, name):
        super(VideoThread, self).__init__()
        self.post_url = post_url
        self.name = name

    def run(self) -> None:
        rsp = requests.get(url=self.post_url, headers=global_headers)
        cookieTmp = cookieStr
        for item in rsp.cookies:
            cookieTmp = cookieTmp + item.name + '=' + item.value + ';'
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Cookie': cookieTmp,
            'Host': 'mooc1.chaoxing.com',
            'Referer': 'https://mooc1.chaoxing.com/ananas/modules/video/index.html?v=2020-1105-2010',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Microsoft Edge";v="90"',
            'sec-ch-ua-mobile': '?0',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36 Edg/90.0.818.51'
        }
        while True:
            print(self.name, requests.get(url=self.post_url, headers=headers).text)
            time.sleep(60)


# 获取课程视频观看总时长
def get_task_status(url: str):
    url = url_302(url)["new_url"]
    result = parse.urlparse(url)
    chapter_data = parse.parse_qs(result.query)
    courseId = chapter_data.get("courseId")[0]
    cpi = chapter_data.get("cpi")[0]
    clazzId = chapter_data.get("clazzid")[0]
    sta_url = "https://stat2-ans.chaoxing.com/task/s/index?courseid={0}&cpi={1}&clazzid={2}&ut=s&".format(courseId, cpi, clazzId)
    rsp = requests.get(url=sta_url, headers=global_headers)
    rsp_html = etree.HTML(rsp.text)
    already_time = float(__list_get(re.findall("[0-9]+[.]?[0-9]?", __list_get(rsp_html.xpath("//div[@class='fl min']/span/text()")))))
    all_time = float(__list_get(re.findall("[0-9]+[.]?[0-9]?", __list_get(rsp_html.xpath("//p[@class='bottomC fs12']/text()")))))
    print(already_time, "/", all_time)
    if already_time < all_time:
        datal_url = "https://stat2-ans.chaoxing.com/task/s/progress/detail?clazzid={0}&courseid={1}&cpi={2}&ut=s&page=1&pageSize=16&status=0".format(clazzId, courseId, cpi)
        rsp = requests.get(url=datal_url, headers=global_headers)
        for i in rsp.json()["data"]["results"]:
            for j in i["list"]:
                if j["type"] == "视频":
                    chapterId = j["chapterId"]
                    break
            if chapterId:
                break
        # print(chapterId)
        cardcount = int(read_cardcount(courseId, clazzId, chapterId, cpi))
        for i in range(cardcount):
            medias_url = "https://mooc1-2.chaoxing.com/knowledge/cards?clazzid={0}&courseid={1}&knowledgeid={2}&num={4}&ut=s&cpi={3}&v=20160407-1".format(clazzId, courseId, chapterId, cpi, i)
            medias_rsp = requests.get(url=medias_url, headers=global_headers)
            medias_HTML = etree.HTML(medias_rsp.text)
            medias_text = medias_HTML.xpath("//script[1]/text()")[0]
            pattern = re.compile(r"mArg = ({[\s\S]*)}catch")
            datas = re.findall(pattern, medias_text)[0]
            datas = json.loads(datas.strip()[:-1])
            for media_item in datas["attachments"]:
                media_type = media_item.get("type")
                jobid = media_item.get("jobid")
                if media_type == "video":
                    objectId = media_item.get("objectId")
                    otherInfo = media_item.get("otherInfo")
                    name = media_item.get('property').get('name')
                    return VideoThread(misson_video(objectId=objectId, otherInfo=otherInfo, jobid=jobid, name=name, reportUrl=datas["defaults"]["reportUrl"], clazzId=clazzId), name=name)
                else:
                    return 0


class video_nomal_thread(threading.Thread):
    def __list_get(self, list: list):
        if len(list):
            return list[0]
        else:
            return ""

    def __init__(self, url):
        super(video_nomal_thread, self).__init__()
        self.url = url
        self.all_time = int(re.findall("duration=\\d+&", url)[0][9:-1])
        self.multimedia_headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Cookie': cookieStr,
            'Host': 'mooc1.chaoxing.com',
            'Referer': 'https://mooc1.chaoxing.com/ananas/modules/video/index.html?v=2020-1105-2010',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Microsoft Edge";v="90"',
            'sec-ch-ua-mobile': '?0',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36 Edg/90.0.818.51'
        }
        self.clazzId = self.__list_get(re.findall("(?<=clazzId=)\\d+", self.url))
        self.duration = self.__list_get(re.findall("(?<=duration=)\\d+", self.url))
        self.objectId = self.__list_get(re.findall("(?<=objectId=)[0-9a-zA-Z]+", self.url))
        self.otherInfo = self.__list_get(re.findall("(?<=otherInfo=)[a-z0-9A-Z_-]+", self.url))
        self.jobid = self.__list_get(re.findall("(?<=jobid=)\\d+", self.url))
        self.uid = self.__list_get(re.findall("(?<=userid=)\\d+", self.url))

    def run(self) -> None:
        rsp = requests.get(url=self.url_replace(0), headers=global_headers)
        print(rsp.status_code)
        cookieTmp = cookieStr
        for item in rsp.cookies:
            cookieTmp = cookieTmp + item.name + '=' + item.value + ';'
        self.multimedia_headers.update({"Cookie": cookieTmp})
        print("线程%s启动中，总任务时长%d秒" % (self.name, self.all_time))
        time_now = 60
        while time_now < self.all_time + 60:
            time.sleep(60)
            rsp = requests.get(url=self.url_replace(time_now), headers=self.multimedia_headers)
            print("线程%s运行中，当前时长:%d ,总时长:%d" % (self.name, time_now, self.all_time))
            time_now = time_now + 60

        rsp = requests.get(url=self.url_replace(self.all_time), headers=self.multimedia_headers)
        print("线程%s执行完成，任务状态:%s" % (self.name, rsp.text))

    def url_replace(self, now_time: int) -> str:
        enc_tmp = encode_enc(self.clazzId, int(self.duration), self.objectId, self.otherInfo, self.jobid, self.uid, str(now_time))
        url_tmp = re.sub("playingTime=\\d+", "playingTime=%d" % now_time, self.url)
        url_tmp = re.sub("enc=[0-9a-zA-Z]+", "enc=%s" % enc_tmp, url_tmp)
        return url_tmp


# 自定义任务类，处理菜单任务
class Things():
    def __init__(self, username='nobody'):
        self.username = username

    def misson_1(self):
        os.system("cls")
        for i in range(len(course_dict)):
            print("%d.%s" % (i + 1, course_dict[i + 1][0]))
        enter = input("\n确认要一键完成以上所有课程吗？(回车确认，任意其他输入则取消并返回主菜单)")
        if enter == "":
            print("开始处理课程中....\n")
            global video_url_list
            video_url_list = []
            for course_item in course_dict:
                print("开始处理'%s'..." % course_dict[course_item][0])
                deal_course_select(course_dict[course_item][1])
                print("'%s' 课程处理完成\n" % course_dict[course_item][0])
            if len(video_url_list) == 0:
                input("\n任务已完成，回车返回主菜单")
            else:
                print("除视频节点外任务已完成，接下来将对剩下的%d个视频节点进行处理" % len(video_url_list))
                speed = input("请选择视频节点的完成方式 1.立即完成(1秒即可完成视频任务点) 2.常规速度完成(完成时间与视频时间等长) :")
                while speed != "1" and speed != "2":
                    print("请输入正常的序号")
                    speed = input("请选择视频节点的完成方式 1.立即完成(1秒即可完成视频任务点) 2.常规速度完成(完成时间与视频时间等长) :")
                if speed == "1":
                    for item in video_url_list:
                        multimedia_headers = {
                            'Accept': '*/*',
                            'Accept-Encoding': 'gzip, deflate, br',
                            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
                            'Connection': 'keep-alive',
                            'Content-Type': 'application/json',
                            'Cookie': cookieStr,
                            'Host': 'mooc1-1.chaoxing.com',
                            'Referer': 'https://mooc1-1.chaoxing.com/ananas/modules/video/index.html?v=2020-0907-1546',
                            'Sec-Fetch-Dest': 'empty',
                            'Sec-Fetch-Mode': 'cors',
                            'Sec-Fetch-Site': 'same-origin',
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36 Edg/85.0.564.51'
                        }
                        rsp = requests.get(url=item.replace("isdrag=0","isdrag=4"), headers=multimedia_headers)
                        print(rsp.text)
                else:

                    video_nomal_thread_pool = []
                    for video_item in video_url_list:
                        video_nomal_thread_pool.append(video_nomal_thread(video_item))
                    for item in video_nomal_thread_pool:
                        item.start()
                        time.sleep(1)
                    print("\n视频线程已全部启动\n")
                    for item in video_nomal_thread_pool:
                        item.join()
                print("任务执行完成")

            print("所有课程处理完成，请手动登陆网站进行查看，如有疑问请联系作者。")
        else:
            pass

    def misson_2(self):
        os.system("cls")
        print("您所加入的课程如下：")
        for i in range(len(course_dict)):
            print("%d.%s" % (i + 1, course_dict[i + 1][0]))
        while True:
            enter = input("输入你要完成的课程序号(输入q回退主菜单)：")
            try:
                if enter == "q":
                    break
                else:
                    try:
                        input("请确认您要完成'%s'" % (course_dict[int(enter)][0]))
                    except:
                        print("'%s'并不是可识别的序号，请您重新检查后输入" % enter)
                        continue
                    global video_url_list
                    video_url_list = []
                    deal_course_select(course_dict[int(enter)][1])
                    if len(video_url_list) == 0:

                        input("\n任务已完成，回车返回主菜单")
                    else:
                        print("除视频节点外任务已完成，接下来将对剩下的%d个视频节点进行处理" % len(video_url_list))
                        speed = input("请选择视频节点的完成方式 1.立即完成(1秒即可完成视频任务点) 2.常规速度完成(完成时间与视频时间等长) :")
                        while speed != "1" and speed != "2":
                            print("请输入正常的序号")
                            speed = input("请选择视频节点的完成方式 1.立即完成(1秒即可完成视频任务点) 2.常规速度完成(完成时间与视频时间等长) :")
                        if speed == "1":
                            for item in video_url_list:
                                multimedia_headers = {
                                    'Accept': '*/*',
                                    'Accept-Encoding': 'gzip, deflate, br',
                                    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
                                    'Connection': 'keep-alive',
                                    'Content-Type': 'application/json',
                                    'Cookie': cookieStr,
                                    'Host': 'mooc1-1.chaoxing.com',
                                    'Referer': 'https://mooc1-1.chaoxing.com/ananas/modules/video/index.html?v=2020-0907-1546',
                                    'Sec-Fetch-Dest': 'empty',
                                    'Sec-Fetch-Mode': 'cors',
                                    'Sec-Fetch-Site': 'same-origin',
                                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36 Edg/85.0.564.51'
                                }
                                rsp = requests.get(url=item.replace("isdrag=0","isdrag=4"), headers=multimedia_headers)
                                print(rsp.text)
                        else:

                            video_nomal_thread_pool = []
                            for video_item in video_url_list:
                                video_nomal_thread_pool.append(video_nomal_thread(video_item))
                            for item in video_nomal_thread_pool:
                                item.start()
                                time.sleep(1)
                            print("\n视频线程已全部启动\n")
                            for item in video_nomal_thread_pool:
                                item.join()
                        print("任务执行完成")

                    break
            except Exception as e:
                print("error:%s" % e)

    def misson_3(self):
        os.system("cls")
        print("您所加入的课程如下：")
        for i in range(len(course_dict)):
            print("%d.%s" % (i + 1, course_dict[i + 1][0]))
        while True:
            enter = input("请输入你要下载资源的课程序号(输入q回退主菜单)：")
            try:
                if enter == "q":
                    break
                else:
                    try:
                        deal_course_all(course_dict[int(enter)][1])
                    except:
                        print("'%s'并不是可识别的序号，请您重新检查后输入" % enter)
                        continue
                    input("\n任务已完成，回车返回主菜单")
                    break
            except Exception as e:
                print("error:%s" % e)

    def misson_4(self):
        os.system("cls")
        print("您所加入的课程如下：")
        for i in range(len(course_dict)):
            print("%d.%s" % (i + 1, course_dict[i + 1][0]))
        while True:
            enter = input("输入你要刷取学习次数的课程序号(输入q回退主菜单)：")
            try:
                if enter == "q":
                    break
                else:
                    try:
                        count = int(input("请输入您要刷取'%s' 的学习次数：" % (course_dict[int(enter)][0])))
                    except:
                        print("错误输入\n")
                        continue
                    try:
                        for num in range(count):
                            set_log(course_dict[int(enter)][1])
                        input("\n任务已完成，回车返回主菜单")
                        break
                    except Exception as e:
                        print(e)
            except Exception as e:
                print("error:%s" % e)

    def misson_5(self):
        os.system("cls")
        threadPool = []
        for i in range(len(course_dict)):
            print("正在读取 %s :" % (course_dict[i + 1][0]))
            isThread = get_task_status(course_dict[i + 1][1])
            if isThread:
                threadPool.append(isThread)

        for i in threadPool:
            i.start()
            time.sleep(10)
        for j in threadPool:
            j.join()

    def misson_6(self):
        os.system("cls")

    def misson_7(self):
        step_1()
        step_2()


class Menu():
    def __init__(self):
        self.thing = Things()
        self.choices = {
            "1": self.thing.misson_1,
            "2": self.thing.misson_2,
            "3": self.thing.misson_3,
            "4": self.thing.misson_4,
            "5": self.thing.misson_5,
            "6": self.thing.misson_6,
            "7": self.thing.misson_7,
            "8": self.quit
        }

    def display_menu(self):
        print("""
菜单：
1.一键完成所有课程中的任务节点(不包含测验)
2.完成单个课程中的所有任务节点(不包含测验)
3.下载课程资源(mp4,pdf,pptx,png等)
4.刷取课程学习次数
5.刷取视频学习时间
6.清除日志
7.退出当前账号，重新登陆
8.退出本程序
        """)

    def run(self):
        while True:
            self.display_menu()
            choice = input("\n请输入您要进行的操作：")
            choice = str(choice).strip()
            action = self.choices.get(choice)
            if action:
                action()
            else:
                print("{0}不是正确的序号，请检查后重新输入".format(choice))

    def quit(self):
        sys.exit(0)


def before_start() -> None:
    print("欢迎您使用 chaoxing_tool , 本工具是针对超星(学习通)所编写的Python脚本工具")
    print("本工具完全免费且开源，项目地址: https://github.com/liuyunfz/chaoxing_tool")
    print("使用前请确认您使用的是最新版，防止因为超星系统更新导致的功能失效")

    print("\n且确认以下须知与功能介绍:")
    print("1.本项目支持一键完成的任务点不包括考试与测试")
    print("2.输入密码时会被自动隐藏，防止您的密码被偷窥")
    print("3.项目不能完全保证不被系统识别异常，请理性使用")
    print("4.所有功能均采用发送GET/POST请求包完成，效率更高且占用资源低")
    print("5.完成课程任务点中的视频任务点会在最后统一处理，由用户决定完成方式")
    print("6.其中快速完成可能会导致异常，而常规完成则会同步视频时长完成（需要保证软件保持开启状态）用于避免可能由时长带来的异常")
    print("7.如果您在使用中有疑问或者遇到了BUG，请前往提交Issue: https://github.com/liuyunfz/chaoxing_tool/issues")

    input("\n回车确认后正式使用本软件:")


if __name__ == "__main__":
    before_start()
    step_1()
    step_2()
    Menu().run()
