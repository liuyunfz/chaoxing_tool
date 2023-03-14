# _*_ coding:utf-8 _*_
# author: liuyunfz

__name__ = "media_download"
__author__ = "liuyunfz"
__disName__ = " 📂 下载课程中的资源"
__description__ = """下载课程章节中的媒体资源
包括视频、Word、PPT、音频等文件
"""

import os
import re
import time

import loguru
import classis.User
from functions.media_download.deal_media import MediaDownload


def run(user: classis.User.User, log):
    os.system("cls")
    for i in range(len(user.course_list)):
        print("%d.%s" % (i + 1, user.course_list[i].course_name))

    course_choice = []
    while not course_choice:
        choice = input("请选择您下载媒体的课程序号，或者输入q退出本功能\n序号:")
        if choice == "q":
            return
        else:
            try:
                course_choice.append(user.course_list[int(choice) - 1])
            except Exception as e:
                log.error("序号输入错误，请尝试重新输入")
                loguru.logger.error(e)
                course_choice.clear()
                pass

    chapter_media = MediaDownload(user, course_choice[0], log)
    chapter_media.deal_course()
    chapter_choice = []
    while not chapter_choice:
        choice = input("请选择将下载资源所在的课程序号，并用逗号分割。\n如果需要读取所有资源则直接回车即可。或者输入q退出本功能\n序号:")
        if not choice:
            chapter_choice = chapter_media.chapter_all
        elif choice == "q":
            return
        else:
            try:
                for i in re.split("[,，]", choice):
                    chapter_choice.append(chapter_media.chapter_all[int(i) - 1])
            except Exception as e:
                log.error("序号输入错误，请尝试重新输入")
                loguru.logger.error(e)
                chapter_choice.clear()
                pass

    media_all = []
    for chapter_item in chapter_choice:
        log.info(f"开始读取章节'{chapter_item.get('name')}'")
        chapter_medias = chapter_media.deal_chapter(chapter_item)
        count = 0
        for _ in chapter_medias:
            _att = _.get("attachments")
            count += len(_att)
            media_all += _att
        log.info(f"章节'{chapter_item.get('name')}'读取完成，共{count}个资源")

    log.success(f"读取完毕，共计{len(media_all)}个资源，即将展示..")
    time.sleep(0.4)
    for media in media_all:
        print(media_all.index(media) + 1, ".", media.get("property").get("name") if media.get("property").get("name") else media.get("property").get("bookname"))
    log.success("资源展示完成")
    while True:
        choice = input("请选择您要下载媒体的序号，用逗号分割，直接回车则全选，或者输入q退出本功能\n序号:")
        try:
            if choice == "q":
                return
            elif choice == '':
                for item in media_all:
                    chapter_media.do_download("./downloads", attachment=item)
            else:
                for i in re.split("[,，]", choice):
                    chapter_media.do_download("./downloads", attachment=media_all[int(i)-1])
        except Exception as e:
            log.error("序号输入错误，请尝试重新输入")
            loguru.logger.error(e)
            pass
    log.success("下载功能执行完毕，回车返回主菜单")
    input()
