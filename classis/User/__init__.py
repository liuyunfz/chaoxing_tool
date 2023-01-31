# _*_ coding:utf-8 _*_
# author: liuyunfz
from utils import doGet, doPost, encrypt_des


class User:
    def __init__(self, username: str = "", password: str = "", cookieStr: str = ""):
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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36 Edg/85.0.564.51',
            'X-Requested-With': 'XMLHttpRequest'
        }
        if cookieStr == "":
            rsp = doPost("https://passport2.chaoxing.com/fanyalogin",
                         headers=self.headers,
                         data="fid=314&uname={0}&password={1}&refer=http%253A%252F%252Fi.mooc.chaoxing.com&t=true"
                         .format(username, encrypt_des(password, "u2oh6Vu^").decode('utf-8')),
                         ifFullBack=True)
            print(rsp.text)
