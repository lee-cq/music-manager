#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@File Name  : importer.py
@Author     : LeeCQ
@Date-Time  : 2023/12/29 21:07

导入器

将Music导入到MusicLib中.

1. 获取被导入的文件的元数据
2. 比对数据库中的元数据
    如果数据库中存在, 则报告存在并跳过
3. 将文件移动到MusicLib中
4. 将元数据写入数据库

"""

import logging
from pathlib import Path

from music_manager.music_lib.models import Music

__all__ = ["import_music"]

logger = logging.getLogger("music_manager.music_lib.importer")


def import_music(file: Path):
    if file.is_file():
        return Music.importer(file.name, file.read_bytes())
    elif file.is_dir():
        for _ in file.iterdir():
            return import_music(_)
    else:
        logger.warning("不支持的文件类型, %s", file)
