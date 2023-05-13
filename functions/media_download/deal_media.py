# _*_ coding:utf-8 _*_
# author: liuyunfz
import json
import os.path
import re
import time

import requests

import classis.User
from functions.deal_mission import DealCourse
from utils import doGet


class MediaDownload(DealCourse):
    def __init__(self, user: classis.User.User, course: classis.User.Course, log):
        super().__init__(user, course, log)
        self.chapter_all = []

    def deal_course(self):
        self.log.info(f"获取'{self.course_name}'课程的章节中...")
        self.course.get_chapter() if not self.course.chapter_list else None
        if self.course.chapter_list:
            self.log.success(f"获取'{self.course_name}'课程章节成功，即将展示")
            time.sleep(0.4)
            self.chapter_all = []
            ind = 1
            for catalog_item in self.course.chapter_list:
                print(catalog_item.get("catalog_name"))
                for chapter_item in catalog_item.get("child_chapter"):
                    print(str(ind) + ". ", "----" * (chapter_item.get("depth") + 1), chapter_item.get("name"))
                    self.chapter_all.append(chapter_item)
                    ind += 1
                print("🔷" * 35)
            self.log.success(f"'{self.course_name}'课程章节展示完毕")
        else:
            self.log.warning(f"'{self.course_name}'课程章节数为零，请核实或检查网络问题。如有出入请反馈issue")

    def deal_chapter(self, chapter_item: dict):
        return super().deal_chapter(chapter_item)

    def read_card_count(self, knowledge_id) -> int:
        return super().read_card_count(knowledge_id)

    def do_download(self, path="", attachment: dict = {}):
        objectid = attachment.get("property").get("objectid")
        name = attachment.get("property").get("name") if attachment.get("property").get("name") else attachment.get("property").get("bookname")
        if objectid is None:
            self.log.error(name + "文件ID获取失败，将跳过该文件")
            return
        _headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Host': 'mooc1-2.chaoxing.com',
            'Referer': 'https://mooc1-2.chaoxing.com/ananas/modules/audio/index.html?v=2022-1028-1705',
            'X-Requested-With': 'XMLHttpRequest'
        }
        download_headers = {
            "referer": "https://mooc1-2.chaoxing.com/ananas/modules/video/index.html?v=2021-0924-1446",
            "Host": "s1.ananas.chaoxing.com"
        }
        download_headers.update(self.user.headers)
        _headers.update(self.user.headers)
        child_path = path + "/" + self.course_name
        if not os.path.exists(path):
            os.mkdir(path)
            os.mkdir(child_path)
        elif not os.path.exists(child_path):
            os.mkdir(child_path)
        _status = doGet(url="https://mooc1-2.chaoxing.com/ananas/status/{}?_dc={}".format(objectid, int(time.time() * 1000)), headers=_headers)
        _status_json = json.loads(_status)
        filename = _status_json.get('filename')
        if _status_json.get("httphd"):
            _url = _status_json.get('httphd')
        elif _status_json.get("pagenum") is not None:
            _url = _status_json.get('pdf')
        else:
            _url = _status_json.get('http')
        with open(path + "/" + self.course_name + '/' + self._get_save_name(name, filename), "wb") as f:
            rsp = requests.get(url=_url, headers=download_headers, stream=True)
            length_already = 0
            length_all = int(rsp.headers['content-length'])
            self.log.info(f"开始下载文件'{name}'")
            for chunk in rsp.iter_content(chunk_size=5242880):
                if chunk:
                    length_already += len(chunk)
                    print("\r下载进度：%d%%" % int(length_already / length_all * 100), end="", flush=True)
                    f.write(chunk)
            print('\n')
            self.log.success(f"'{name}'下载完成")

    def _get_save_name(self, name: str, filename: str):
        """

        :param name:
        :param filename:
        :return:
        """
        _end = '.' + filename.split('.')[-1]
        name = re.sub('([\/:*?"<>|])*','',name)
        _l = name.split(".")
        if len(_l) == 1:
            return name + _end
        else:
            if re.fullmatch('([a-z0-9]{1,7})', _l[-1]):
                return ''.join(_l[:-1]) + _end
            else:
                return name + _end
