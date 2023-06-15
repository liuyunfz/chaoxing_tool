# _*_ coding:utf-8 _*_
# author: liuyunfz
import time

import loguru

import classis.User
from classis.Media.Live import Live
from classis.Media.Video import Video
from classis.SelfException import RequestException
from functions.deal_mission import DealCourse
from utils import doGet


class DealVideo:

    def __init__(self, user: classis.User.User, course: classis.User.Course, log):
        self.user = user
        self.course = course
        self.log = log

    @staticmethod
    def run_video(video: Video, user, log, all_time: int = 0):
        video_status = video.get_status()
        if video_status:
            duration = video_status.get('duration')
            dtoken = video_status.get('dtoken')
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
                'Referer': 'https://mooc1.chaoxing.com/ananas/modules/video/index.html?v=2023-0519-2354'
            }
            _headers.update(user.headers)
        else:
            raise RequestException("视频状态获取失败")
            return

        _url = video.get_url(0, duration, dtoken, 3)
        _rsp = doGet(_url, _headers)
        loguru.logger.debug(_rsp)
        time_all = round(duration / 60, 2)
        time_m = duration // 60 if all_time == 0 else int(all_time)
        time_s = duration - time_m * 60
        for i in range(time_m):
            time.sleep(59.8)
            _url = video.get_url(i * 60 + 59, duration, dtoken, 0)
            log.info(f"'{video.name}'当前刷取时长{i + 1}分钟,总时长{time_all}分钟")
            _rsp = doGet(_url, _headers)
            loguru.logger.debug(_rsp)
        if time_s:
            time.sleep(time_s)
            _url = video.get_url(duration, duration, dtoken, 4)
            log.info(f"'{video.name}'当前刷取时长{time_all}分钟,总时长{time_all}分钟")
            _rsp = doGet(_url, _headers)
            loguru.logger.debug(_rsp)

    @staticmethod
    def run_live(live: Live, user, log):
        live_status = live.get_status()
        if live_status:
            duration = live_status.get("temp").get("data").get('duration')
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
            _headers.update(user.headers)
        else:
            raise RequestException("直播状态获取失败")
            return
        _dis = (duration + 59) // 60
        for i in range(int(_dis)):
            log.info(f"'{live.name}'当前刷取时长{i + 1}分钟,总时长{_dis}分钟")
            live.do_finish()
            time.sleep(59)

    def get_videos(self):
        """
        获得该课程的所有视频对象
        :return:
        """
        _data = self.course.get_progress_data()
        _video_list = []
        for i in _data:
            for j in i['list']:
                if j['type'] == '视频':
                    _dc = DealCourse(self.user, self.course, self.log)
                    attachments = _dc.deal_chapter({'knowledge_id': j.get("chapterId")})
                    for attach_item in attachments:
                        medias = attach_item.get("attachments")
                        defaults = attach_item.get("defaults")
                        for media in medias:
                            media_type = media.get("type")
                            media_module = media.get('property').get('module')
                            media_name = media.get('property').get('name')
                            if media_type == "video":
                                if media_module == "insertaudio":
                                    pass
                                else:
                                    _video_list.append(Video(media, self.user.headers, defaults, name=media_name))
        return _video_list
