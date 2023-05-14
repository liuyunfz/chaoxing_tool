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
        self.name = self.attachment.get("property").get("title")

    def do_finish(self):
        _stream_name = self.attachment.get("property").get("streamName")
        _vdoid = self.attachment.get("property").get("vdoid")
        _url = "https://zhibo.chaoxing.com/saveTimePc?streamName={0}&vdoid={1}&userId={2}&isStart=0&t=1680790434506&courseId={3}".format(
            _stream_name, _vdoid, self.defaults.get("userid"), self.courseId)
        _rsp = doGet(url=_url, headers=self.headers)
        loguru.logger.debug(_rsp)
        if _rsp == "@success":
            return True
        else:
            return False

    def get_status(self) -> 'dict|None':
        status_url = f"https://mooc1.chaoxing.com/ananas/live/liveinfo?liveid={self.attachment.get('property').get('liveId')}&userid={self.defaults.get('userid')}&clazzid={self.defaults.get('clazzId')}&knowledgeid={self.defaults.get('knowledgeid')}&courseid={self.courseId}&jobid={self.attachment.get('property').get('_jobid')}&ut=s"
        mission_headers = {
            "Referer": "https://mooc1.chaoxing.com/ananas/modules/live/index.html?v=2022-1214-1139"
        }
        mission_headers.update(self.headers)
        status_text = doGet(url=status_url, headers=mission_headers)
        try:
            status_json = json.loads(status_text)
            return status_json
        except Exception as e:
            loguru.logger.error(e)
            return