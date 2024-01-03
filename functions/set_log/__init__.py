# _*_ coding:utf-8 _*_

__name__ = "set_log"
__author__ = "liuyunfz"
__disName__ = " 📜 刷取课程学习次数"
__description__ = """刷取课程的学习次数，但请注意
由于程序的高速访问，可能会造成预期次数与实际次数的较大误差
请自行检验并多次刷取以达到最终效果
"""

import os
import time

import loguru
from config import GloConfig
import classis.User
from utils import doGet


def run(user: classis.User.User, log):
    os.system("cls")
    for i in range(len(user.course_list)):
        print("%d.%s" % (i + 1, user.course_list[i].course_name))
    delay = GloConfig.data.get("FunConfig").get("set-log").get("delay")
    while True:
        choice = input("请选择您要刷取学习次数的课程序号，或者输入q退出本功能\n序号:")
        if choice == 'q':
            return
        try:
            course = user.course_list[int(choice) - 1]
            log.info(f"当前课程'{course.course_name}'学习次数共{course.get_count_log()}次")
            times = int(input("请输入要刷取的学习次数:"))
            _url = course.get_url_log()
            for i in range(1, times + 1):
                log.info(f"正在刷取'{course.course_name}'课程第{i}次")
                _rsp = doGet(url=_url, headers=user.headers)
                loguru.logger.info(_rsp)
                time.sleep(delay)
            log.success("课程学习次数刷取完毕")
            log.info(f"当前课程'{course.course_name}'学习次数共{course.get_count_log()}次")
            input("回车返回主菜单")
            return
        except Exception as e:
            loguru.logger.error(e)
            log.error("课程序号输入错误，请重新尝试\n")
            continue
