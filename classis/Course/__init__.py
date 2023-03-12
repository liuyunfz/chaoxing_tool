# _*_ coding:utf-8 _*_
# author: liuyunfz
import re
import time
from urllib import parse
from loguru import logger
from lxml import etree

from utils import doGet, xpath_first


class Course:
    def __init__(self, course_id: str, class_id: str, url: str, course_name: str, course_author: str, cpi: str = ""):
        self.course_id = course_id
        self.class_id = class_id
        self.url = url
        self.course_name = course_name
        self.course_author = course_author
        if cpi == "":
            self.cpi = parse.parse_qs(parse.urlparse(self.url).query).get("cpi")[0]
        self.chapter_list = []
        self.mission_all = 0
        self.mission_fn = 0
        self._child_chapter_list = []
        self.url_log = ""

    def __str__(self) -> str:
        return "\n".join([f"CourseName: {self.course_name}",
                          f"Author: {self.course_author}",
                          f"Url: {self.url}",
                          f"CourseId: {self.course_id}",
                          f"ClazzId: {self.class_id}",
                          f"Cpi: {self.cpi}"])

    def get_chapter(self, headers):
        self.chapter_list.clear()
        html_text = doGet(url=f"https://mooc2-ans.chaoxing.com/mooc2-ans/mycourse/studentcourse?courseid={self.course_id}&clazzid={self.class_id}&cpi={self.cpi}&ut=s&t={int(time.time())}", headers=headers)
        ele = etree.HTML(html_text)
        ele_root = xpath_first(ele, "//div[@class='fanyaChapterWhite']")
        self.mission_all = 0
        self.mission_fn = int(xpath_first(ele_root, "./div[1]/h2/span/text()"))
        logger.info(f"mission_finished/mission_all: {self.mission_fn}/{self.mission_all}")
        ele_units = ele_root.xpath("./div[2]/div[@class='chapter_td']/div[@class='chapter_unit']")
        for unit in ele_units:
            unit_catalog_name = xpath_first(unit, "./div[1]/div[1]/div[@class='catalog_name']/span/text()").strip()
            """
            {
                1计算机系统概论
                    1.1 计算机系统简介    1
                    1.1.1 计算机的软硬件概念    2
                    1.1.2 计算机系统的层次结构    2
                    1.2 计算机的基本组成    1
                    1.2.1 冯·诺依曼计算机的特点   2
                
            },{
                2计算机的发展及应用
                    2.1 计算机的发展史    1
                    2.1.1 计算机的产生和发展    2
                    2.1.2 微型计算机的出现和发展    2
                    2.1.3 软件技术的兴起和发展    2
                    2.2 计算机的应用    1
            }
            """
            for item_li in unit.xpath("./div[2]/ul/li"):
                self.__recursion_chapter_item(item_li, 0)
            logger.debug(self._child_chapter_list)
            self.chapter_list.append({
                "catalog_name": unit_catalog_name,
                "child_chapter": self._child_chapter_list.copy()
            })
            self._child_chapter_list.clear()

    def __recursion_chapter_item(self, element, depth: int):
        self._child_chapter_list.append({
            "name": xpath_first(element, "./div[1]/div[1]/div[@class='catalog_name']").xpath('string(.)').strip(),
            "depth": depth,
            "knowledge_id": xpath_first(element, "./div/@onclick").split("'")[3],
            "job_count": int(xpath_first(element, "./div[1]/div[1]/div[@class='catalog_task']/input/@value") or "0")

        })
        chapter_list = element.xpath("./ul/li")
        if chapter_list:
            for chapter_item in chapter_list:
                self.__recursion_chapter_item(chapter_item, depth + 1)

    def get_url_log(self, headers: dict) -> str:
        """
        获得课程记录学习的链接，同时更新课程的URL
        :param headers: 访问的请求头
        :return: 课程学习记录的URL
        """
        if not self.url_log:
            self.url = f"https://mooc2-ans.chaoxing.com/mooc2-ans/mycourse/studentcourse?courseid={self.course_id}&clazzid={self.class_id}&cpi={self.cpi}&ut=s&t=1678608658539"
            _rsp = doGet(url=self.url, headers=headers)
            self.url_log = re.findall("(https://fystat-ans.chaoxing.com/log/setlog(.)+)\"></script>", _rsp)[0][0]
        return self.url_log
