# _*_ coding:utf-8 _*_
# author: liuyunfz
import json
import random
import re
import threading
import time

import loguru
from lxml import etree

from config import GloConfig
from classis.Media.Book import Book
from classis.Media.Document import Document
from classis.Media.Live import Live
from classis.Media.Read import Read
from classis.Media.Video import Video
from utils import doGet, doPost, xpath_first
import classis.User


class DealCourse:
    def __init__(self, user: classis.User.User, course: classis.User.Course, log):
        self.user = user
        self.course = course
        self.log = log
        self.course_name = course.course_name
        self.class_id = course.class_id
        self.course_id = course.course_id
        self.cpi = course.cpi
        self.mission_list = []
        self.video_mode = GloConfig.data.get("FunConfig").get("deal-mission").get("video-mode")
        self.single_thread = GloConfig.data.get("FunConfig").get("deal-mission").get("single-thread")
        self.thread_pool = []

    def do_finish(self):
        if not self.course.ifOpen:
            self.log.warning("本课程已结课或锁定，将自动跳过")
            return
        from functions.set_time import DealVideo
        self.deal_course()
        self.thread_pool.clear()
        if self.mission_list:
            self.log.info(f"共读取到 {len(self.mission_list)} 个章节待完成")
            for mission_item in self.mission_list:
                self.log.info(f"开始处理章节'{mission_item.get('name')}'")
                attach_list = self.deal_chapter(mission_item)
                if attach_list:
                    for attach_item in attach_list:
                        medias = attach_item.get("attachments")
                        defaults = attach_item.get("defaults")
                        for media in medias:
                            if media.get("job") is None:
                                continue
                            media_type = media.get("type")
                            media_module = media.get('property').get('module')
                            media_name = media.get('property').get('name')
                            finish_status = False
                            if media_type == "video":
                                if media_module == "insertaudio":
                                    self.log.info(f"开始处理音頻任务点:{media_name}")
                                    finish_status = Video(media, self.user.headers, defaults, "Audio").do_finish()
                                else:
                                    self.log.info(f"开始处理视频任务点:{media_name}")
                                    _video = Video(media, self.user.headers, defaults, name=media_name)
                                    if self.video_mode == 0:
                                        finish_status = _video.do_finish()
                                    else:
                                        _thread = threading.Thread(target=DealVideo.run_video, args=(_video, self.user, self.log))
                                        if self.single_thread:
                                            self.log.info(f"检测到您启动了单线程模式")
                                            self.log.info(f"开始刷取视频任务点'{media_name}'，每分钟更新进度")
                                            _thread.start()
                                            _thread.join()
                                        else:

                                            self.thread_pool.append(_thread)
                                            self.log.info(f"视频任务点'{media_name}'，已根据您的配置启动等时长刷取线程")
                                            _thread.start()
                                            time.sleep(random.random() + 0.5)

                                        continue

                            elif media_type == "read":
                                self.log.info(f"开始处理阅读任务点:{media_name}")
                                finish_status = Read(media, self.user.headers, defaults, self.course_id).do_finish()
                            elif media_type == "document":
                                self.log.info(f"开始处理Doc文件任务点:{media_name}")
                                finish_status = Document(media, self.user.headers, defaults, self.course_id).do_finish()
                            elif media_type == "live":
                                _live = Live(media, self.user.headers, defaults, self.course_id)
                                _thread = threading.Thread(target=DealVideo.run_live, args=(_live, self.user, self.log))
                                self.thread_pool.append(_thread)
                                self.log.info(f"直播任务点'{_live.name}'，已自动启动等时长刷取线程")
                                _thread.start()
                                continue

                            elif "bookname" in media.get("property"):
                                self.log.info(f"开始处理图书任务点:{media_name}")
                                finish_status = Book(media, self.user.headers, defaults, self.course_id).do_finish()
                            else:
                                self.log.error(f"检测到不支持的任务点类型:{media_type}")
                                loguru.logger.info(media)
                                continue

                            if finish_status:
                                self.log.success(f"任务点'{media_name}'完成成功")
                            else:
                                self.log.error(f"任务点'{media_name}'完成失败")

    def deal_course(self):
        self.mission_list.clear()
        self.log.info(f"获取'{self.course_name}'课程的章节中...")
        self.course.get_chapter()
        if self.course.chapter_list:
            self.log.success(f"获取'{self.course_name}'课程章节成功，即将展示")
            time.sleep(0.4)
            for catalog_item in self.course.chapter_list:
                print(catalog_item.get("catalog_name"))
                for chapter_item in catalog_item.get("child_chapter"):
                    print("----" * (chapter_item.get("depth") + 1), chapter_item.get("name"), self.mission_list.append(chapter_item) or f"    ✍待完成任务点 {chapter_item.get('job_count')}" if chapter_item.get("job_count") else "")
                print("🔷" * 35)
            self.log.success(f"'{self.course_name}'课程章节展示完毕")
        else:
            self.log.warning(f"'{self.course_name}'课程章节数为零，请核实或检查网络问题。如有出入请反馈issue")

    def deal_chapter(self, chapter_item: dict):
        """
        处理章节内容，获得章节的具体任务点

        :param chapter_item: 章节dict
        :return: 返回媒体list
        """
        page_count = self.read_card_count(chapter_item.get("knowledge_id"))
        attach_list = []
        for page in range(page_count):
            try:
                medias_url = "https://mooc1.chaoxing.com/knowledge/cards?clazzid={0}&courseid={1}&knowledgeid={2}&num={4}&ut=s&cpi={3}&v=20160407-1".format(self.class_id, self.course_id, chapter_item.get("knowledge_id"), self.cpi, page)
                medias_rsp = doGet(url=medias_url, headers=self.user.headers)
                medias_HTML = etree.HTML(medias_rsp)
                medias_text = xpath_first(medias_HTML, "//body/script[1]/text()")
                datas_raw = re.findall(r"mArg = ({[\s\S]*)}catch", medias_text).pop()
                datas = json.loads(datas_raw.strip()[:-1])
                attach_list.append(datas)
            except:
                continue
        return attach_list

    def read_card_count(self, knowledge_id) -> int:
        """
        获取章节总页码数

        :param knowledge_id: 章节id
        :return: 返回该章节的页数
        """
        _url = 'https://mooc1.chaoxing.com/mycourse/studentstudyAjax?'
        data = "courseId={0}&clazzid={1}&chapterId={2}&cpi={3}&verificationcode=&mooc2=1".format(self.course_id, self.class_id, knowledge_id, self.cpi)
        rsp = doGet(url=_url + data, headers=self.user.headers)
        rsp_HTML = etree.HTML(rsp)
        return int(xpath_first(rsp_HTML, "//input[@id='cardcount']/@value"))
