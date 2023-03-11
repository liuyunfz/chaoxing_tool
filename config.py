# _*_ coding:utf-8 _*_
# author: liuyunfz

import yaml


class GloConfig:
    data: dict = None

    @staticmethod
    def init_yaml_data():
        with open("config.yml", "r", encoding="utf-8") as f:
            GloConfig.data = yaml.safe_load(f)

    @staticmethod
    def release_yaml_data():
        with open("config.yml", "w", encoding="utf-8") as f:
            GloConfig.data = yaml.safe_dump(GloConfig.data, f, encoding='utf-8', allow_unicode=True, sort_keys=False)
