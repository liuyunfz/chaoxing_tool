# _*_ coding:utf-8 _*_
# author: liuyunfz
import json

import loguru

from classis.Media import Media
from utils import doGet


class Video(Media):
    def __init__(self, attachment: dict, headers, defaults: dict, dtype: str = "Video", name: str = ""):
        super().__init__(attachment, headers)
        self.objectId = attachment.get("objectId")
        self.reportUrl = defaults.get("reportUrl")
        self.defaults = defaults
        self.dtype = dtype
        self.name = name

    def get_status(self) -> 'dict|None':
        status_url = "https://mooc1-1.chaoxing.com/ananas/status/{}?k=&flag=normal&_dc=1600850935908".format(self.objectId)
        mission_headers = {
            "Referer": "https://mooc1.chaoxing.com/ananas/modules/video/index.html?v=2022-0329-1945"
        }
        mission_headers.update(self.headers)
        status_text = doGet(url=status_url, headers=mission_headers)
        try:
            status_json = json.loads(status_text)
            return status_json
        except Exception as e:
            loguru.logger.error(e)
            return

    def do_finish(self):
        video_status = self.get_status()
        if video_status:
            duration = video_status.get('duration')
            dtoken = video_status.get('dtoken')
            _url = self.get_url(duration, duration, dtoken, 4)
            _headers = {
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
                'Connection': 'keep-alive',
                'Content-Type': 'application/json',
                'Sec-Fetch-Dest': 'empty',
                'Host': 'mooc1.chaoxing.com',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'Referer': 'https://mooc1.chaoxing.com/ananas/modules/video/index.html?v=2023-0203-1904'
            }
            _headers.update(self.headers)
            _rsp = doGet(url=_url, headers=_headers)
            loguru.logger.debug(_rsp)
            if json.loads(_rsp).get("isPassed"):
                return True
            else:
                return False

    def get_url(self, time_end: int, duration: int, dtoken: str, play_type: int) -> str:
        """
        获得视频记录提交的链接

        :param time_end: 结束的时间，默认为duration，即总时长
        :param duration: 总时长
        :param dtoken: 视频的dtoken参数
        :param play_type: 视频的播放状态
        :return: 提交地址
        """
        import hashlib
        import time
        enc_raw = "[{0}][{1}][{2}][{3}][{4}][{5}][{6}][0_{7}]". \
            format(self.defaults.get("clazzId"), self.defaults.get("userid"), self.jobid, self.objectId, int(time_end) * 1000, "d_yHJ!$pdA~5", duration * 1000, duration)
        enc = hashlib.md5(enc_raw.encode()).hexdigest()
        url_former = self.reportUrl
        url_later = "/{0}?clazzId={1}&playingTime={2}&duration={10}&clipTime=0_{10}&objectId={3}&otherInfo={4}&jobid={5}&userid={6}&isdrag={9}&view=pc&enc={7}&rt=0.9&dtype={11}&_t={8}". \
            format(dtoken, self.defaults.get("clazzId"), time_end, self.objectId, self.attachment.get("otherInfo"), self.jobid, self.defaults.get("userid"), enc, int(time.time() * 1000), play_type, duration, self.dtype)
        return url_former + url_later
