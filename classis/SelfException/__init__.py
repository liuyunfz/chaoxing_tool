# _*_ coding:utf-8 _*_
# author: liuyunfz
import requests


class LoginException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class RequestException(Exception):
    def __init__(self, html: requests.Response, method: int = 0):
        self.html = html
        self.method = method
        self.text = html.text

    def __str__(self):
        return "\n".join([f"Url: {self.html.url}",
                          f"Method: {['Get', 'Post'][self.method]}",
                          f"Status: {self.html.status_code}"])
        # + f"Html: {self.html.text}"
