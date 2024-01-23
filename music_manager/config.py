#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@File Name  : config.py.py
@Author     : LeeCQ
@Date-Time  : 2023/12/29 19:37

"""
from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings

__all__ = ["Settings", "settings"]

from sys import stderr

import confuse


class IncludeLazyConfig(confuse.LazyConfig):
    """A version of Confuse's LazyConfig that also merges in data from
    YAML files specified in an `include` setting.
    """

    def read(self, user=True, defaults=True):
        super().read(user, defaults)

        try:
            for view in self["include"]:
                self.set_file(view.as_filename())
        except confuse.NotFoundError:
            pass
        except confuse.ConfigReadError as err:
            stderr.write("configuration `import` failed: {}".format(err.reason))


class FastAPIConfig(BaseModel):
    """"""
    enable: bool = False


class FeishuConfig(BaseModel):
    """"""
    enable: bool = False


class Settings(BaseSettings):
    # 项目名称
    app_name: str = "music_manager"
    # 项目版本
    app_version: str = "1.0.0"
    # 项目作者
    PROJECT_AUTHOR: str = "LeeCQ"
    # 项目作者邮箱
    PROJECT_AUTHOR_EMAIL: str = "lee-cq@qq.com"
    # Music Library
    music_library: Path = Path(__file__).parent.parent.joinpath("music_library")
    # 数据目录
    data_dir: Path = Path(__file__).parent.parent.joinpath("data")

    fastapi_config: FastAPIConfig = FastAPIConfig()
    feishu_config: FeishuConfig = FeishuConfig()


config = IncludeLazyConfig("music_manager", __name__)
# settings = Settings(**config)
settings = Settings()
