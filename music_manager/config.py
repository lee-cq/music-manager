#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@File Name  : config.py.py
@Author     : LeeCQ
@Date-Time  : 2023/12/29 19:37

"""
import builtins
from pathlib import Path

from pydantic_settings import BaseSettings

__all__ = ["Settings", "settings"]


def settings():
    try:
        return getattr(builtins, "music_settings")
    except AttributeError:
        _s = Settings()
        setattr(builtins, "music_settings", _s)
        return Settings()


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
