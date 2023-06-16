# _*_ coding:utf-8 _*_
# author: liuyunfz
from abc import abstractmethod


class Media:
    def __init__(self, attachment: dict, headers):
        self.name = ""
        self.attachment = attachment
        self.type = attachment.get("type")
        self.jobid = attachment.get("jobid")
        self.headers = {
            # "Cookie": headers.get("Cookie"),
            "User-Agent": headers.get("User-Agent")
        }

    @abstractmethod
    def do_finish(self):
        pass
