# _*_ coding:utf-8 _*_

__name__ = "set_time"
__author__ = "liuyunfz"
__disName__ = " ⏳ 刷取课程视频观看时长"
__description__ = """刷取课程中视频的观看时长
首先读取课程中的所有视频资源
然后由用户选择要通过哪个视频进行时长刷取
默认针对第一个视频文件进行观看时长的刷取
"""

import os
import re
import threading

import loguru
import classis.User
from .deal_time import DealVideo


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
                time_list = course.get_time_log()
                log.info(f"当前课程'{course.course_name}'视频总时长共{time_list[1]}分钟,已学习{time_list[0]}分钟")
                if time_list[0] < time_list[1]:
                    _dis = time_list[1] - time_list[0]
                    log.info(f"目标刷取时长:{_dis}分钟,即将开始...")
                else:
                    log.info(f"课程时长已充足，请选择其他课程")
                    continue
                _videos = DealVideo(user, course, log).get_videos()
                if len(_videos) == 0:
                    log.error("未获取到有效的课程视频，请手动检查章节是否被锁")
                    continue
                for item in _videos:
                    print(f"{_videos.index(item)}.{item.name}")
                _video_choice = re.split("[,，]", input("请选择要刷取时长的视频序号并以逗号分隔,直接回车默认选择第一个,-1则全部选择\n序号:"))
                thread_pool = []
                if len(_video_choice) == 1:
                    if _video_choice[0] == "-1":
                        for item in _videos:
                            _thread = threading.Thread(target=DealVideo.run_video, args=(item, user, log))
                            thread_pool.append(_thread)
                            _thread.start()
                    elif _video_choice[0] == "":
                        _thread = threading.Thread(target=DealVideo.run_video, args=(_videos[0], user, log, _dis))
                        thread_pool.append(_thread)
                        _thread.start()
                    else:
                        _thread = threading.Thread(target=DealVideo.run_video, args=(_videos[int(_video_choice[0])], user, log, _dis))
                        thread_pool.append(_thread)
                        _thread.start()
                else:
                    for i in _video_choice:
                        _thread = threading.Thread(target=DealVideo.run_video, args=(_videos[int(i)], user, log))
                        thread_pool.append(_thread)
                        _thread.start()
                for _t in thread_pool:
                    _t.join()
                log.success("课程学习时长刷取完毕")
                log.info(f"当前课程'{course.course_name}'学习时长共{course.get_time_log()[0]}分支")
                input("回车返回主菜单")
        except Exception as e:
            loguru.logger.error(e)
            log.error("课程序号输入错误，请重新尝试\n")
            continue
