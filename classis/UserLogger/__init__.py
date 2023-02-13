# _*_ coding:utf-8 _*_
# author: liuyunfz
from loguru import logger
import sys


class UserLogger:
    def __init__(self):
        logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | <level>{message}</level>",
                   filter=lambda record: record["extra"].get("name") == "a")
        self.log_self = logger.bind(name="a")

    def info(self, message: str):
        self.log_self.info(message)

    def error(self, message: str):
        self.log_self.error(message)

    def success(self, message: str):
        self.log_self.success(message)

    def warning(self, message: str):
        self.log_self.warning(message)
