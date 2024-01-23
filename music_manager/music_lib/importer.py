#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@File Name  : importer.py
@Author     : LeeCQ
@Date-Time  : 2023/12/29 21:07

导入器

将Music导入到MusicLib中
"""

__all__ = ["import_music"]

import logging
from pathlib import Path

from music_manager.music_lib.models import Music

logger = logging.getLogger("music_manager.music_lib.importer")


def import_music(file: Path):
    if file.is_file():
        return Music.importer(file.name, file.read_bytes())
    elif file.is_dir():
        for _ in file.iterdir():
            return import_music(_)
    else:
        logger.warning("不支持的文件类型, %s", file)
