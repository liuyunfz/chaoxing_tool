# _*_ coding:utf-8 _*_
# author: liuyunfz

from utils import doGet
import classis.User


def deal_course(user: classis.User.User, course: classis.User.Course):
    course.get_chapter(user.headers)
