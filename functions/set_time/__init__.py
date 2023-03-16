# _*_ coding:utf-8 _*_

__name__ = "set_time"
__author__ = "liuyunfz"
__disName__ = " ⏳ 刷取课程视频观看时长"
__description__ = """刷取课程中视频的观看时长
首先读取课程中累计观看时长和总时长
随后默认针对第一个视频文件进行观看时长的刷取
"""

import os
import time

import loguru

from classis.Media.Video import Video
from config import GloConfig
import classis.User
from functions.deal_mission import DealCourse
from utils import doGet


def run(user: classis.User.User, log):
    os.system("cls")
    for i in range(len(user.course_list)):
        print("%d.%s" % (i + 1, user.course_list[i].course_name))
    while True:
        choice = input("请选择您要刷取视频时长的课程序号，或者输入q退出本功能\n序号:")
        try:
            if choice == 'q':
                return
            else:
                course = user.course_list[int(choice) - 1]
                time_list = course.get_time_log(user.headers)
                log.info(f"当前课程'{course.course_name}'视频总时长共{time_list[1]}分钟,已学习{time_list[0]}分钟")
                if time_list[0] < time_list[1]:
                    _dis = time_list[1] - time_list[0]
                    log.info(f"目标刷取时长:{_dis}分钟,即将开始...")
                else:
                    log.info(f"课程时长已充足，请选择其他课程")
                    continue
                _video = get_video(user, course, log)
                video_status = _video.get_status()
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
                        'Referer': 'https://mooc1.chaoxing.com/ananas/modules/video/index.html?v=2023-0203-1904'
                    }
                    _headers.update(user.headers)
                for i in range(int(_dis)):
                    log.info(f"当前刷取时长:{i}分钟,总时长{_dis}分钟")
                    _url = _video.get_url(i * 60 % duration + 60, duration, dtoken, 3)
                    _rsp = doGet(_url, _headers)
                    loguru.logger.debug(_rsp)
                    time.sleep(59)

                log.success("课程学习次数刷取完毕")
                log.info(f"当前课程'{course.course_name}'学习次数共{course.get_count_log(user.headers)}次")
                input("回车返回主菜单")
        except Exception as e:
            loguru.logger.error(e)
            log.error("课程序号输入错误，请重新尝试\n")
            continue


def get_video(user: classis.User.User, course, log):
    """
    获得该课程的第一个视频对象
    :param user:
    :param course:
    :return:
    """
    _data = course.get_progress_data(user.headers)
    for i in _data:
        for j in i['list']:
            if j['type'] == '视频':
                _dc = DealCourse(user, course, log)
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
                                return Video(media, user.headers, defaults)
