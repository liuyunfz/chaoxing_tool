# _*_ coding:utf-8 _*_
# author: liuyunfz
import requests
from loguru import logger
from requests import post, get
import yaml
import pyDes
import binascii
from time import sleep
from classis.SelfException import RequestException
from lxml.etree import _ElementUnicodeResult
with open("config.yml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)
    glo_headers = config.get("GloConfig").get("headers")
    glo_timeout = config.get("GloConfig").get("timeout")
    logger.success("Loaded config successfully")
    if_delay = config.get("GloConfig").get("delay").get("enable")
    time_delay = config.get("GloConfig").get("delay").get("time")

ses = requests.session()


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
        ses.headers.clear()
        ses.headers.update(headers)
        sleep(time_delay) if if_delay else None
        html = ses.get(url=url, timeout=glo_timeout)
        if ifFullBack:
            return html
        if html.status_code == 200:
            return html.text
        else:
            raise RequestException(html, 0)

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
        logger.debug("With data: %s" % data)
        ses.headers.clear()
        ses.headers.update(headers)
        sleep(time_delay) if if_delay else None
        html = ses.post(url=url, data=data, timeout=glo_timeout)
        if ifFullBack:
            return html
        if html.status_code == 200:
            return html.text
        else:
            raise RequestException(html, 1)

    except Exception as e:
        logger.error(f"Post Url {url} Error\n {e}")


def xpath_first(element, path):
    """
    返回xpath获取到的第一个元素，如果没有则返回空字符串
    由于 lxml.etree._Element._Element 为私有类，所以不予设置返回值类型

    :param element: etree.HTML实例
    :param path: xpath路径
    :return: 第一个元素或空字符串
    """
    if type(element) in (str, int):
        return element
    res = element.xpath(path)
    if type(res) == _ElementUnicodeResult:
        return res
    if len(res) == 1:
        return res[0]
    else:
        return ""


def direct_url(old_url: str, headers: dict, ifLoop: bool = False) -> str:
    """
    返回重定向后的真实Url

    :param old_url: 待重定向的链接地址
    :param headers: 附带的请求头
    :param ifLoop: 是否迭代查询直至无跳转
    :return: 最终的Url
    """
    logger.debug("Redirect old url: %s" % old_url)
    location_new = None
    try:
        while location_new is None:
            rsp = requests.get(url=old_url, headers=headers, allow_redirects=False)
            location_new = rsp.headers.get("Location")
            if ifLoop:
                return location_new | old_url
            if location_new is None:
                logger.debug("Final url: %s" % old_url)
                return old_url
            else:
                old_url = location_new
                location_new = None
    except Exception as e:
        logger.error(e)
        return ""


def encrypt_des(msg, key):
    des_obj = pyDes.des(key, key, pad=None, padmode=pyDes.PAD_PKCS5)
    secret_bytes = des_obj.encrypt(msg, padmode=pyDes.PAD_PKCS5)
    return binascii.b2a_hex(secret_bytes)


if __name__ == '__main__':
    doGet("https://www.6yfz.cn/")
