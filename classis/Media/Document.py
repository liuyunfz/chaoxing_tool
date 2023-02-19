# _*_ coding:utf-8 _*_
# author: liuyunfz
import json
import time

import loguru

from classis.Media import Media
from utils import doGet


class Document(Media):
    def __init__(self, attachment: dict, headers, defaults: dict, courseId: str):
        super().__init__(attachment, headers)
        self.defaults = defaults
        self.courseId = courseId

    def do_finish(self):
        _headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Connection': 'keep-alive',
            'Host': 'mooc1-2.chaoxing.com',
            'Referer': 'https://mooc1-2.chaoxing.com/ananas/modules/pdf/index.html?v=2020-1103-1706',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36 Edg/87.0.664.52',
            'X-Requested-With': 'XMLHttpRequest'
        }
        _headers.update(self.headers)
        _url = 'https://mooc1-2.chaoxing.com/ananas/job/document?jobid={0}&knowledgeid={1}&courseid={2}&clazzid={3}&jtoken={4}&_dc={5}'.format(
            self.jobid, self.defaults.get("knowledgeid"), self.courseId, self.defaults.get("clazzId"), self.attachment.get("jtoken"), int(time.time() * 1000))
        _rsp = doGet(url=_url, headers=_headers)
        loguru.logger.debug(_rsp)
        if json.loads(_rsp).get("status"):
            return True
        else:
            return False