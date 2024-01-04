# _*_ coding:utf-8 _*_

__name__ = "deal_mission"
__author__ = "liuyunfz"
__disName__ = " ✅ 一键完成课程中的任务节点"
__description__ = """一键完成所有课程或所选课程中需要完成的任务点
包括视频、阅读、PPT、音频等
但不包括测验与考试

注：视频节点将根据配置文件中的设置，自动选择立刻完成还是等时长速刷取
"""

import os
import re
import time

import loguru

from .deal_course import DealCourse
from utils import clear_console
import classis.User


def run(user: classis.User.User, log):
    clear_console()
    for i in range(len(user.course_list)):
        print("%d.%s" % (i + 1, user.course_list[i].course_name))

    course_choice = []
    while not course_choice:
        choice = input("请选择您要完成的课程序号，并用逗号分割。\n如果需要全部完成全部课程则直接回车即可。或者输入q退出本功能\n序号:")
        if choice == "":
            course_choice = user.course_list
        elif choice == "q":
            return
        else:
            try:
                for i in re.split("[,，]", choice):
                    course_choice.append(user.course_list[int(i) - 1])
            except Exception as e:
                log.error("序号输入错误，请尝试重新输入")
                loguru.logger.error(e)
                course_choice.clear()
                pass

    log.info("开始处理课程中....\n")
    video_url_list = []
    for course_item in course_choice:
        log.info("开始处理'%s'..." % course_item.course_name)
        _deal_course = DealCourse(user, course_item, log)
        _deal_course.do_finish()
        for item in _deal_course.thread_pool:
            item.join()
        log.success("'%s' 课程处理完成\n" % course_item.course_name)
        time.sleep(0.4)
    if len(video_url_list) == 0:
        log.success("任务已完成，回车返回主菜单")
        input()
