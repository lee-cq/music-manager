#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@File Name  : router.py
@Author     : LeeCQ
@Date-Time  : 2023/12/22 22:04

"""
import logging
from pathlib import Path
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from music_manager.apis.models import ResponseModel, File, MusicId3, ResourceModify
from music_manager.music_lib.music_resource import MusicResource

router = APIRouter()

logger = logging.getLogger("task.router")


class FileListBody(BaseModel):
    file_path: Path
    sorted_fields: list[Any] = []


@router.post("/token/")
def token():
    """获取token"""
    return {"token": 123}


@router.get("/record/")
def record():
    """获取record"""
    return {"record": 123}


@router.post("/file_list/")
def file_list(body: FileListBody):
    """列出文件夹下的文件"""
    file_path = Path(body.file_path)
    if not file_path.exists() or not file_path.is_dir():
        return ResponseModel(code="400", message="文件不存在 OR 不是一个目录", result=False)
    _dir = File(
        children=[
            File(
                children=[] if _.is_dir() else None,
                icon="icon-folder" if _.is_dir() else "icon-script-file",
                id=_id + 1,
                name=_.name,
                title=_.name,
                size=_.stat().st_size,
            )
            for _id, _ in enumerate(file_path.iterdir())
        ],
        icon="icon-folder",
        id=0,
        name=file_path.name,
        title=file_path.name,
    )
    return ResponseModel(data=[_dir])


class MusicId3Body(BaseModel):
    file_path: Path
    file_name: str


@router.post("/music_id3/")
def music_id3(body: MusicId3Body):
    """获取音乐文件的元信息"""
    full_path = body.file_path.joinpath(body.file_name)
    if full_path.suffix in ["txt", "lrc"]:
        return ResponseModel()
    if body.file_path == body.file_name:
        return ResponseModel()
    if not full_path.exists() or full_path.suffix not in [".flac", ".mp3", ".wav"]:
        return ResponseModel(code="400", message="文件不存在", result=False)

    return ResponseModel(data=MusicId3.from_ffprobe(full_path))


class FetchId3ByTitleBody(BaseModel):
    """{
    "title":"莉莉安",
    "resource":"qmusic",
    "full_path":"/Users/lcq/Music/KwMusic/flac/宋冬野-莉莉安.flac"
    }"""

    title: str
    resource: ResourceModify
    full_path: Path


@router.post("/fetch_id3_by_title/")
async def fetch_id3_by_title(body: FetchId3ByTitleBody):
    """根据歌曲名获取音乐文件的元信息"""
    title = body.title
    if body.resource == "acoustid":
        title = body.full_path
    elif body.resource == "smart_tag":
        title = {"title": title, "full_path": body.full_path}

    data = await MusicResource(body.resource).fetch_id3_by_title(title)
    return ResponseModel(
        data=data,
    )


class FetchLyricBody(BaseModel):
    """{"song_id":"002WMf1v4FFbm9","resource":"qmusic"}"""

    song_id: str
    resource: ResourceModify


@router.post("/fetch_lyric/")
async def fetch_lyric(body: FetchLyricBody):
    """获取歌词"""
    return ResponseModel(
        data=await MusicResource(body.resource).fetch_lyric(body.song_id),
    )


@router.post("/translation_lyc")
def translation_lyc():
    """翻译歌词"""
    pass


@router.post("/tidy_folder")
def tidy_folder():
    """整理文件夹"""
    pass


class RequestUpdateId3(BaseModel):
    music_id3_info: list[MusicId3]


@router.post("/update_id3")
def update_id3(body: RequestUpdateId3):
    """更新音乐文件的元信息"""
    for _music_id3 in body.music_id3_info:
        if not _music_id3.file_full_path.exists():
            logger.warning("文件不存在: %s", _music_id3.file_full_path)
            continue
        _music_id3.save()


# def file_list(self, request, *args, **kwargs):
# def music_id3(self, request, *args, **kwargs):
# def update_id3(self, request, *args, **kwargs):
# def batch_update_id3(self, request, *args, **kwargs):
# def batch_auto_update_id3(self, request, *args, **kwargs):
# def fetch_lyric(self, request, *args, **kwargs):
# def fetch_id3_by_title(self, request, *args, **kwargs):
# def translation_lyc(self, request, *args, **kwargs):
# def tidy_folder(self, request, *args, **kwargs):
# def upload_image(self, request, *args, **kwargs):
# def clear_celery(self, request, *args, **kwargs):
# def active_queue(self, request, *args, **kwargs):
# def task1(self, request, *args, **kwargs):
# def task2(self, request, *args, **kwargs):
# def full_scan_folder(self, request, *args, **kwargs):
