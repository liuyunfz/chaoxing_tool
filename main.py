# _*_ coding:utf-8 _*_
# author: liuyunfz
import yaml
import os
from loguru import logger
import sys
import importlib
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

    sign_status = False
    if sign_mode == "1" or sign_mode == "":
        while not sign_status:
            try:
                username = input("\n请输入您的用户名(手机号):")
                password = input("请输入您的密码:")
                user = User(username, password)
                logger.debug(user)
                log.success("恭喜你 %s,登录成功" % user.name)
                sign_status = True
            except Exception as e:
                log.error(e)
    else:
        pass  # TODO 完善cookie登录与判断
    log.info("运行读取课程任务")
    user.getCourse()
    log.success("课程读取成功")
    if not user.course_list:
        log.info("读取到您没有可执行的课程，如果与您的实际情况不符请提交issue")
        exit()

    functions = []
    path_list = os.listdir('./functions')
    for module_path in path_list:
        logger.debug("Loading function %s" % module_path)
        functions.append(importlib.import_module("functions.%s" % module_path))
        logger.success("Loaded %s successfully" % module_path)

    menu_str = "菜单"
    for fun_ind in range(len(functions)):
        menu_str += f"\n{fun_ind + 1}.{functions[fun_ind].__disName__}"

    while True:
        try:
            print(menu_str)
            fun_i = int(input("\n请输入您要使用功能的序号:"))
            func = functions[fun_i-1]
            os.system("cls")
            print("\n".join([f"功能名称: {func.__disName__}",
                             f"作者: {func.__author__}",
                             f"使用须知: {func.__description__}"])
                  )
            if input("\n回车确认使用本功能，其他输入则会退回主菜单:") == "":
                func.run(user, log)
            else:
                os.system("cls")
                continue

        except Exception as e:
            log.error("功能调用失败，请检查输入的功能序号")
            logger.error(e)
