# _*_ coding:utf-8 _*_
# author: liuyunfz
import requests
from loguru import logger
from requests import post, get
import yaml
import pyDes
import binascii

with open("config.yml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)
    glo_headers = config.get("GloConfig").get("headers")
    glo_timeout = config.get("GloConfig").get("timeout")
    logger.success("loading config success")


def doGet(url: str, headers: 'dict|str' = glo_headers, ifFullBack: bool = False) -> 'str|requests.Response':
    """
    调用requests进行Get请求，并输出日志

    :param url: 欲访问的链接地址
    :param headers: 请求携带的headers，默认为config文件中GloConfig.headers
    :param ifFullBack 是否返回完整的Response信息
    :return: 返回网页文本信息，即html.text
    """
    try:
        logger.debug("Do Get to Url %s" % url)
        html = get(url=url, headers=headers)
        if ifFullBack:
            return html
        if html.status_code == 200:
            return html.text
        else:
            raise BaseException("网页状态码返回不正确:%s" % html.status_code)

    except Exception as e:
        logger.error(f"Get Url {url} Error\n {e}")


def doPost(url: str, headers: 'dict|str' = glo_headers, data: 'dict|str' = "", ifFullBack: bool = False) -> 'str|requests.Response':
    """
    调用requests进行Post请求，并输出日志

    :param url: 欲访问的链接地址
    :param headers: 请求携带的headers，默认为config文件中GloConfig.headers
    :param data: 请求携带的data数据，默认为空
    :param ifFullBack 是否返回完整的Response信息
    :return: 返回网页文本信息，即html.text
    """
    try:
        logger.debug("Do Post to Url %s" % url)
        html = post(url=url, headers=headers, data=data, timeout=glo_timeout)
        if ifFullBack:
            return html
        if html.status_code == 200:
            return html.text
        else:
            raise BaseException("网页状态码返回不正确:%s" % html.status_code)

    except Exception as e:
        logger.error(f"Post Url {url} Error\n {e}")


def encrypt_des(msg, key):
    des_obj = pyDes.des(key, key, pad=None, padmode=pyDes.PAD_PKCS5)
    secret_bytes = des_obj.encrypt(msg, padmode=pyDes.PAD_PKCS5)
    return binascii.b2a_hex(secret_bytes)


if __name__ == '__main__':
    doGet("https://www.6yfz.cn/")
