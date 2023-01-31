# _*_ coding:utf-8 _*_
# author: liuyunfz
import yaml
import os
from loguru import logger
import sys
from classis.User import User
from classis.UserLogger import UserLogger
from utils import *

if __name__ == '__main__':
    logger.remove()
    with open("config.yml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    config_debug = config.get("GloConfig").get("debug")
    infoStr = config.get("InfoStr")
    if config_debug.get("enable"):
        logger.add(sys.stdout, format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
                   filter=lambda record: record["extra"].get("name") != "a",
                   level=config_debug.get("level"))
    log = UserLogger()

    os.system("cls")
    print(infoStr.get("instructions"))
    input("\n回车确认后正式使用本软件:")
    os.system("cls")
    sign_mode = input(infoStr.get("signStr"))
    while sign_mode not in ["1", "2", ""]:
        print("\n" + infoStr.get("errSignMode"))
        sign_mode = input(infoStr.get("signStr"))
    if sign_mode == "1" or sign_mode == "":
        username = input("\n请输入您的用户名(手机号):")
        password = input("请输入您的密码:")
        user = User(username, password)
