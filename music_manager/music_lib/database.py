#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@File Name  : database.py
@Author     : LeeCQ
@Date-Time  : 2023/12/24 21:14

"""
from sqlmodel import create_engine

from music_manager.config import data_dir


__all__ = ["engine", "init"]

engine = create_engine(
    f"sqlite:///{data_dir.joinpath('data.db')}",
    echo=True,
    pool_size=5,
    connect_args={"check_same_thread": False},
)


def init():
    from music_manager.music_lib.models import SQLModel, Music, MusicBrainZMapping

    SQLModel.metadata.create_all(engine)


if __name__ == "__main__":
    init()
