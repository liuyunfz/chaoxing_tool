# _*_ coding:utf-8 _*_
# author: liuyunfz
from urllib import parse
from loguru import logger


class Course:
    def __init__(self, course_id: str, class_id: str, url: str, course_name: str, course_author: str, cpi: str = ""):
        self.course_id = course_id
        self.class_id = class_id
        self.url = url
        self.course_name = course_name
        self.course_author = course_author
        if cpi == "":
            self.cpi = parse.parse_qs(parse.urlparse(self.url).query).get("cpi")[0]

    def __str__(self) -> str:
        return "\n".join([f"CourseName: {self.course_name}",
                          f"Author: {self.course_author}",
                          f"Url: {self.url}",
                          f"CourseId: {self.course_id}",
                          f"ClazzId: {self.class_id}",
                          f"Cpi: {self.cpi}"])
