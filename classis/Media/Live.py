# _*_ coding:utf-8 _*_
# author: liuyunfz
import json
import time
from urllib import parse

import loguru
from lxml import etree

from classis.Media import Media
from utils import doGet, xpath_first


class Live(Media):
    def __init__(self, attachment: dict, headers, defaults: dict, courseId: str):
        super().__init__(attachment, headers)
        self.defaults = defaults
        self.courseId = courseId

    def do_finish(self):
        token_url = 'https://live.chaoxing.com/courseLive/newpclive?streamName=' + self.attachment.get("property").get("streamName") + '&vdoid=' + self.attachment.get("property").get("vdoid") + '&width=630&height=530' + '&jobid=' + self.jobid + '&userId={0}&knowledgeid={1}&ut=s&clazzid={2}&courseid={3}'.format(
            self.defaults.get("knowledgeid"), self.defaults.get("clazzId"), self.courseId)
        token_rsp = doGet(url=token_url, headers=self.headers)
        token_url = xpath_first(etree.HTML(token_rsp), "//iframe/@src")
        token = parse.parse_qs(parse.urlparse(token_url).query).get("token")
        _url = "https://zhibo.chaoxing.com/live/saveCourseJob?courseId={0}&knowledgeId={1}&classId={2}&userId={3}&jobId={4}&token={5}".format(
            self.courseId, self.defaults.get("knowledgeid"), self.defaults.get("clazzId"), self.defaults.get("userid"), self.jobid, token[0])
        _rsp = doGet(url=_url, headers=self.headers)
        loguru.logger.debug(_rsp)
        if json.loads(_rsp).get("status"):
            return True
        else:
            return False
