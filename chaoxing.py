#!/usr/bin/env python
# _*_ coding:utf-8 _*_
import requests,base64,os,sys,time
from lxml import etree
def encode_enc(clazzid:str,duration:int,objectId:str,otherinfo:str,jobid:str,userid:str):
    import hashlib
    data="[{0}][{1}][{2}][{3}][{4}][{5}][{6}][0_{7}]".format(clazzid,userid,jobid,objectId,duration*1000,"d_yHJ!$pdA~5",duration*1000,duration)
    print(data)
    return hashlib.md5(data.encode()).hexdigest()
def sign_in(uname:str,password:str):
    sign_in_url="https://passport2.chaoxing.com/fanyalogin"
    sign_in_data="fid=314&uname={0}&password={1}&refer=http%253A%252F%252Fi.mooc.chaoxing.com&t=true".format(uname,base64.b64encode(password.encode("utf-8")).decode("utf-8"))
    sign_in_headers={
        'Accept':'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding':'gzip, deflate, br',
        'Accept-Language':'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Connection':'keep-alive',
        'Content-Length':'98',
        'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
        'Cookie':'route=3744838b34ea6b4834cd438e19ed44f0; JSESSIONID=9CD969F9C1B9633A46EAD7880736DD51; fanyamoocs=11401F839C536D9E; fid=314; isfyportal=1; ptrmooc=t', 
        'Host':'passport2.chaoxing.com',
        'Origin':'https://passport2.chaoxing.com',
        'Referer':'https://passport2.chaoxing.com/login?loginType=4&fid=314&newversion=true&refer=http://i.mooc.chaoxing.com',
        'Sec-Fetch-Dest':'empty',
        'Sec-Fetch-Mode':'cors',
        'Sec-Fetch-Site':'same-origin',
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36 Edg/85.0.564.51',
        'X-Requested-With':'XMLHttpRequest'
    }
    sign_in_rsp=requests.post(url=sign_in_url,data=sign_in_data,headers=sign_in_headers)
    return sign_in_rsp
def step_1():
    sign_sus=False
    while sign_sus==False :
        os.system("cls")
        uname=input("请输入您的手机号:")
        import getpass
        password=getpass.getpass("请输入您的密码:")
        sign_in_rsp=sign_in(uname,password)
        sign_in_json=sign_in_rsp.json()
        if sign_in_json['status'] == False:
            print(sign_in_json['msg2'],"\n\n请按回车重新键入账号数据")
            input()
        else:
            sign_sus=True
            print("登陆成功，正在处理您的数据...")           
    global cookieStr,uid
    uid=sign_in_rsp.cookies['_uid']
    cookieStr = '' 
    for item in sign_in_rsp.cookies:
        cookieStr = cookieStr + item.name + '=' + item.value + ';'
def step_2():
    class_url="http://mooc1-2.chaoxing.com/visit/courses"
    class_headers={
        'Cookie':cookieStr,
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36 Edg/85.0.564.51'
    }
    class_rsp=requests.get(url=class_url,headers=class_headers)
    if class_rsp.status_code==200:
        class_HTML=etree.HTML(class_rsp.text)
        os.system("cls")
        print("处理成功，您当前已开启的课程如下：\n")
        i=0
        global course_dict
        course_dict={}
        for class_item in class_HTML.xpath("/html/body/div/div[2]/div[3]/ul/li[@class='courseItem curFile']"):
            #courseid=class_item.xpath("./input[@name='courseId']/@value")[0]
            #classid=class_item.xpath("./input[@name='classId']/@value")[0]
            try:              
                class_item_name=class_item.xpath("./div[2]/h3/a/@title")[0]
                #等待开课的课程由于尚未对应链接，所有缺少a标签。
                i+=1
                print(class_item_name)
                course_dict[i]=[class_item_name,"https://mooc1-2.chaoxing.com{}".format(class_item.xpath("./div[1]/a[1]/@href")[0])]
            except:
                pass
        print("———————————————————————————————————")
    else:
        print("课程处理失败，请联系作者")
    #print(course_dict)
def deal_course(url:str):
    course_302_url=url
    course_headers={
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding':'gzip, deflate, br',
        'Accept-Language':'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Connection':'keep-alive',
        'Cookie':cookieStr,
        'Host':'mooc1-2.chaoxing.com',
        'Sec-Fetch-Dest':'document',
        'Sec-Fetch-Mode':'navigate',
        'Sec-Fetch-Site':'none',
        'Upgrade-Insecure-Requests':'1',
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36 Edg/85.0.564.51'
    }
    #302跳转，requests库默认追踪headers里的location进行跳转，使用allow_redirects=False
    course_302_rsp=requests.get(url=course_302_url,headers=course_headers,allow_redirects=False)
    course_rsp=requests.get(url=course_302_rsp.headers['Location'],headers=course_headers)
    course_HTML=etree.HTML(course_rsp.text)
    #为防止账号没有课程或没有班级，需要后期在xpath获取加入try，以防报错
    chapter_mission=[]
    try:
        for course_unit in course_HTML.xpath("/html/body/div[5]/div[1]/div[2]/div[3]/div"):
            print(course_unit.xpath("./h2/a/@title")[0])
            for chapter_item in course_unit.xpath("./div"):
                chapter_status=chapter_item.xpath("./h3/span[@class='icon']/em/@class")[0]
                if chapter_status == "orange":
                    print("----",chapter_item.xpath("./h3/span[@class='articlename']/a/@title")[0],"      ",chapter_item.xpath("./h3/span[@class='icon']/em/text()")[0])
                    chapter_mission.append("https://mooc1-2.chaoxing.com{}".format(chapter_item.xpath("./h3/span[@class='articlename']/a/@href")[0]))
                else:    
                    print("----",chapter_item.xpath("./h3/span[@class='articlename']/a/@title")[0],"      ",chapter_item.xpath("./h3/span[@class='icon']/em/@class")[0])
    except:
        pass
    print("课程读取完成，共有%d个章节可一键完成"%len(chapter_mission))
    deal_misson(chapter_mission)
def deal_misson(missons:list):
    from urllib import parse
    for chapter_mission_item in missons:
        result = parse.urlparse(chapter_mission_item)
        chapter_data=parse.parse_qs(result.query)
        medias_url="https://mooc1-2.chaoxing.com/knowledge/cards?clazzid={0}&courseid={1}&knowledgeid={2}&num=0&ut=s&cpi=149176464&v=20160407-1".format(chapter_data.get('clazzid')[0],chapter_data.get('courseId')[0],chapter_data.get('chapterId')[0])
        class_headers={
        'Cookie':cookieStr,
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36 Edg/85.0.564.51'
        }
        medias_rsp=requests.get(url=medias_url,headers=class_headers)
        medias_HTML=etree.HTML(medias_rsp.text)
        medias_text=medias_HTML.xpath("//script[1]/text()")[0]
        import re,json
        pattern = re.compile(r'attachments":([\s\S]*),"defaults"') 
        re_result=re.findall(pattern,medias_text)[0]
        reportUrl=re.findall(r'reportUrl":([\s\S]*),"chapterCapture"',medias_text)[0]
        reportUrl=reportUrl.replace("\"","")
        result_json=json.loads(re_result)
        for video_item in result_json:
            if video_item.get("isPassed") == True:
                pass
            else:
                if video_item.get("type") == "video":
                    objectId=video_item.get("objectId")
                    otherInfo=video_item.get("otherInfo")
                    jobid=video_item.get("jobid")
                    name=video_item.get('property').get('name')
                    status_url="https://mooc1-1.chaoxing.com/ananas/status/{}?k=&flag=normal&_dc=1600850935908".format(objectId)
                    status_rsp=requests.get(url=status_url,headers=class_headers)
                    status_json=json.loads(status_rsp.text)
                    duration=status_json.get('duration')
                    dtoken=status_json.get('dtoken')
                    print(objectId,otherInfo,jobid,uid,name,duration,reportUrl)
                    multimedia_headers={
                        'Accept':'*/*',
                        'Accept-Encoding':'gzip, deflate, br',
                        'Accept-Language':'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
                        'Connection':'keep-alive',
                        'Content-Type':'application/json',
                        'Cookie':cookieStr,
                        'Host':'mooc1-1.chaoxing.com',
                        'Referer':'https://mooc1-1.chaoxing.com/ananas/modules/video/index.html?v=2020-0907-1546',
                        'Sec-Fetch-Dest':'empty',
                        'Sec-Fetch-Mode':'cors',
                        'Sec-Fetch-Site':'same-origin',
                        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36 Edg/85.0.564.51'
                    }
                    import time
                    elses="/{0}?clazzId={1}&playingTime={2}&duration={2}&clipTime=0_{2}&objectId={3}&otherInfo={4}&jobid={5}&userid={6}&isdrag=4&view=pc&enc={7}&rt=0.9&dtype=Video&_t={8}".format(dtoken,chapter_data.get('clazzid')[0],duration,objectId,otherInfo,jobid,uid,encode_enc(chapter_data.get('clazzid')[0],duration,objectId,otherInfo,jobid,uid),int(time.time()*1000))
                    reportUrl_item=reportUrl+str(elses)
                    print(reportUrl_item)
                    multimedia_rsp=requests.get(url=reportUrl_item,headers=multimedia_headers)
                    print(multimedia_rsp.text)
class Things():
    def __init__(self, username='nobody'):
        self.username = username

    def misson_1(self):
        os.system("cls")
        for i in range(len(course_dict)):
            print("%d.%s"%(i+1,course_dict[i+1][0]))
        enter=input("\n确认要一键完成以上所有课程吗？(回车确认，任意其他输入则取消并返回主菜单)")
        if enter == "":
            print("开始处理课程中....\n")
            for course_item in course_dict:
                print("开始处理'%s'..."%course_item[0])
                deal_course(course_item[1])
                print("'%s' 课程处理完成\n"%course_item[0])
            print("所有课程处理完成，请手动登陆网站进行查看，如有疑问请联系作者。")
        else:
            pass
    def misson_2(self):
        os.system("cls")
        print("您所加入的课程如下：")
        for i in range(len(course_dict)):
            print("%d.%s"%(i+1,course_dict[i+1][0]))       
        break_loop=False
        while break_loop == False:
            enter=input("输入你要完成的课程序号(输入q回退主菜单)：")
            try:
                input("请确认您要完成'%s'"%(course_dict[int(enter)][0]))
                deal_course(course_dict[int(enter)][1])
                input("\n任务已完成，回车返回主菜单")
                break_loop=True
            except:
                if enter == "q":
                    break_loop=True
                    pass
                else:
                    print("'%s'并不是可识别的序号，请您重新检查后输入"%enter)

    def misson_3(self):
        step_1()
        step_2()
        Menu().run()



class Menu():
    def __init__(self):
        self.thing = Things()
        self.choices = {
            "1": self.thing.misson_1,
            "2": self.thing.misson_2,
            "3": self.thing.misson_3,
            "4": self.quit
        }

    def display_menu(self):
        print("""
菜单：
1.一键完成所有课程视频
2.完成单个课程中的所有视频
3.退出当前账号，重新登陆
4.退出本程序
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


if __name__ == "__main__":
    step_1()
    step_2()
    Menu().run()

'''
var isdrag = 0;
    switch (evt) {
    case "play":
        isdrag = 3;
        break;
    case "pause":
        isdrag = 2;
        break;
    case "ended":
        isdrag = 4;
        break
'''

