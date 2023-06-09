# _*_ coding:utf-8 _*_
# author: liuyunfz
import json
import re
import requests
import sys

from ..SelfException import LoginException, RequestException
from ..Course import Course
from lxml import etree
from loguru import logger

from utils import doGet, doPost, encrypt_des, xpath_first, direct_url

from config import GloConfig


class User:
    def __init__(self, username: str = "", password: str = "", cookieStr: str = ""):
        self.course_list = []
        self.headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Host': 'passport2.chaoxing.com',
            'Origin': 'https://passport2.chaoxing.com',
            'Referer': 'https://passport2.chaoxing.com/login?loginType=4&fid=314&newversion=true&refer=http://i.mooc.chaoxing.com',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': GloConfig.data.get("GloConfig").get("headers").get("User-Agent"),
            'X-Requested-With': 'XMLHttpRequest'
        }
        if cookieStr == "":
            self.username = username
            rsp = doPost("https://passport2.chaoxing.com/fanyalogin",
                         headers=self.headers,
                         data="fid=314&uname={0}&password={1}&refer=http%253A%252F%252Fi.mooc.chaoxing.com&t=true"
                         .format(username, encrypt_des(password, "u2oh6Vu^").decode('utf-8')),
                         ifFullBack=True)
            if rsp.status_code == 200:
                rsp_json = json.loads(rsp.text)
                if rsp_json.get("status"):
                    self.name = rsp_json.get("name")
                    self.uid = rsp.cookies.get('_uid')
                    for item in rsp.cookies:
                        cookieStr = cookieStr + item.name + '=' + item.value + ';'
                    self.cookieStr = cookieStr
                    self.headers = {
                        'User-Agent': GloConfig.data.get("GloConfig").get("headers").get("User-Agent"),
                        # "Cookie": cookieStr
                    }
                else:
                    raise LoginException(rsp_json.get("msg2"))
            else:
                raise RequestException(rsp, 1)
        else:
            self.cookieStr = cookieStr
            self.headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36 Edg/85.0.564.51',
                "Cookie": cookieStr
            }
            if self.__checkLogin():
                self.uid = re.findall(r"_uid=(\d+);", self.cookieStr)[0] if re.findall(r"_uid=(\d+);", self.cookieStr) else ""
                self.name = self.uid  # 获取意义不大，暂不添加
                self.username = self.uid
            else:
                raise LoginException("Cookie失效，请重新获取")

    def __checkLogin(self) -> bool:
        _url = "https://i.chaoxing.com/base/settings?t=1677930825027"
        _headers = {
            'Refer': 'https://i.chaoxing.com/base?t=1677930160468'
        }
        _headers.update(self.headers)
        _rsp = requests.get(url=_url, headers=_headers, allow_redirects=False)
        if _rsp.status_code == 200:
            return True
        else:
            return False

    def __str__(self):
        return "\n".join([f"Uid: {self.uid}",
                          f"Username: {self.username}",
                          f"Cookie: {self.cookieStr}"])

    def getCourse(self):
        self.course_list.clear()
        html = doGet(url="https://mooc2-ans.chaoxing.com/mooc2-ans/visit/courses/list?v=1675234609566&rss=1&start=0&size=500&catalogId=0&superstarClass=0&searchname=", headers=self.headers)
        ele = etree.HTML(html)
        course_ele = ele.xpath("//ul[@id='courseList']/li")
        for item in course_ele:
            tmp_url = xpath_first(item, "./div[2]/h3/a/@href")
            if tmp_url.startswith("http"):
                # 如果为自己教授的课则无协议头
                course = Course(xpath_first(item, "./div[1]/input[@class='courseId']/@value"),
                                xpath_first(item, "./div[1]/input[@class='clazzId']/@value"),
                                # direct_url(tmp_url, self.headers),    具体调用课程后再更新URL，避免多余的HTTP操作
                                tmp_url,
                                xpath_first(item, "./div[2]/h3/a/span/@title"),
                                xpath_first(item, "./div[2]/p[@class='line2 color3']/@title"),
                                headers=self.headers
                                )
                logger.debug("Add course:\n" + str(course))
                self.course_list.append(course)
