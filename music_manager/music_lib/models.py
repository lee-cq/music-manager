#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@File Name  : models.py
@Author     : LeeCQ
@Date-Time  : 2023/12/24 18:14

"""
import datetime
from pathlib import Path
from typing import Optional
from uuid import UUID
from enum import Enum

from sqlmodel import SQLModel, Field, Session

from music_manager.apis.models import MusicId3
from music_manager.music_lib.database import engine
from music_manager.config import settings

__all__ = ["Music", "MusicBrainZMapping", "BrainZModify", "SQLModel"]

settings = settings()


class BrainZModify(str, Enum):
    artist = "artist"  # 艺术家
    album = "album"  # 专辑
    track = "track"  # 音轨
    recording = "recording"  # 歌曲
    release = "release"  # 发布
    work = "work"  # 作品


class Music(MusicId3, table=True):
    """"""

    __tablename__ = "music_table"

    id: Optional[int] = Field(default=None, primary_key=True)

    def save_to_db(self):
        with Session(engine) as session:
            session.add(self)
            session.commit()
            session.refresh(self)

    @classmethod
    def importer(cls, filename: str, data: bytes):
        """导入器"""
        settings.data_dir.joinpath("cache").mkdir(parents=True, exist_ok=True)
        cache_file = settings.data_dir.joinpath("cache", filename)
        cache_file.write_bytes(data)
        music_file = settings.music_library.joinpath(filename)
        if music_file.exists():
            raise FileExistsError("文件已存在")
        self = cls.from_mutagen(cache_file)
        self.file_full_path = music_file
        self.save_to_db()

        MusicBrainZMapping.add(BrainZModify.artist, self.artist)
        MusicBrainZMapping.add(BrainZModify.album, self.album)
        MusicBrainZMapping.add(BrainZModify.recording, self.title)
        cache_file.rename(cache_file)
        return self


class MusicBrainZMapping(SQLModel, table=True):
    """MusicBrainZ的信息映射表，缓存信息"""

    __tablename__ = "music_brain_z_mapping"

    id: Optional[int] = Field(default=None, primary_key=True)
    type: BrainZModify
    name: str
    uuid: UUID = Field(None, unique=True, nullable=True)
    value: str | None = Field(None)
    update_time: datetime.datetime

    def save_to_db(self):
        with Session(engine) as session:
            session.add(self)
            session.commit()
            session.refresh(self)

    @classmethod
    def add(cls, type_, name: str):
        """"""

        self = cls(type=type_, name=name, update_time=datetime.datetime.now())
        self.save_to_db()
        return self


if __name__ == "__main__":
    from sqlmodel import create_engine

    engine = create_engine("sqlite:///test.sqlite3", echo=True)
    SQLModel.metadata.create_all(engine, checkfirst=True)
