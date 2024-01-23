#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@File Name  : models.py
@Author     : LeeCQ
@Date-Time  : 2023/12/22 22:23

"""
import base64
import datetime
from pathlib import Path
from typing import Optional, Literal, Any

from sqlmodel import SQLModel, Field

from music_manager.music_lib.ffmpeg_operator import get_music_artwork
from music_manager.music_lib.model_ffmpeg import FfprobrModel

NoneType = type(None)

FileIconModel = Literal[
    "icon-folder",
    "icon-script-file",
    "icon-music",
    "icon-video",
    "icon-picture",
    "icon-doc",
    "icon-zip",
]

ResourceModify = Literal[
    "smart_tag",  # 智能标签
    "netease",  # 音乐ID3
    "migu",  # 咪咕
    "qmusic",  # QQ音乐
    "kugou",  # 酷狗
    "kuwo",  # 酷我
    "acoustid",  # AcoustID
]

MusicIDModify = Literal[
    "tag",
    "format",
    "artwork",
]


class File(SQLModel):
    children: list["File"] | None = []
    icon: FileIconModel
    id: int
    name: str
    title: str
    size: int | None = None
    state: str | None = None
    update_time: Optional[datetime.datetime] = None


class MusicId3(SQLModel):
    """"""

    # File 相关
    file_full_path: Path | None = Field(None, description="文件全路径, Path")
    filename: str | None = Field(None, description="文件名, Path.name")
    size: int | None = Field(None, description="大小 - format")

    # 数据库相关
    id: int | None = None  # 数据库 ID
    uuid: str | None = Field(None, description="musicbrainz上的Music UUID")

    # Music 相关
    title: str = Field(None, description="歌曲名 - tag")
    artist: str = Field(None, description="歌手 - tag")
    lyrics: str | None = Field(None, description="歌词 - tag")
    year: int | None = Field(None, description="年份 - tag")
    comment: str | None = Field(None, description="备注 - tag")
    genre: str | None = Field(None, description="风格 - tag")

    # 专辑相关
    tracknumber: int | None = Field(None, description="音轨 - tag")
    discnumber: int | None = Field(None, description="碟片 - tag")
    album: str | None = Field(None, description="专辑 - tag")
    album_type: str | None = Field(None, description="专辑类型 - tag")
    albumartist: str | None = Field(None, description="专辑艺术家 - tag")

    # Stream相关
    duration: float | None = Field(None, description="时长 - format")
    bit_rate: int | None = Field(None, description="码率 - format")

    # 封面相关
    artwork: str | None = Field(None, description="封面 Base64 Image")
    artwork_w: int | None = Field(None, description="封面宽高 - Video Stream")
    artwork_h: int | None = Field(None, description="封面宽高 - Video Stream")
    artwork_size: int | None = Field(None, description="封面占用空间 - 计算得到")

    language: str | None = Field(None, description="语言 - tag")

    @staticmethod
    def property_type(name: str) -> MusicIDModify:
        """

        :param name:
        :return: tag, format, artwork
        """
        if name.startswith("artwork"):
            return "artwork"
        elif name in ["duration", "size", "bit_rate"]:
            return "format"
        return "tag"

    @classmethod
    def from_ffprobe(cls, music_path: str | Path):
        music_path = Path(music_path)
        try:
            artwork = base64.b64encode(get_music_artwork(music_path)).decode()
            artwork_size = len(artwork)
            artwork = "data:image/jpeg;base64," + artwork
        except RuntimeError:
            artwork = None
            artwork_size = None
        ffprobe: FfprobrModel = FfprobrModel.from_media_file(music_path)
        return cls(
            title=ffprobe.format.tags.title,  # tag
            artist=ffprobe.format.tags.artist,  # tag
            year=ffprobe.format.tags.year,  # tag
            comment=ffprobe.format.tags.comment,  # tag
            lyrics=ffprobe.format.tags.lyrics,  # tag
            duration=ffprobe.format.duration,  # format
            size=ffprobe.format.size,  # format
            bit_rate=ffprobe.format.bit_rate,  # format
            tracknumber=0,  # tag CD Track Number
            discnumber=0,  # tag CD Disc Number
            artwork=artwork,  # 封面: get_music_artwork
            artwork_w=ffprobe.stream_video[0].width,  # video stream
            artwork_h=ffprobe.stream_video[0].height,  # video stream
            artwork_size=artwork_size,  # 封面大小，计算得到
            album=ffprobe.format.tags.album,  # tag
            album_type=ffprobe.format.tags.album_type,  # tag
            genre=ffprobe.format.tags.genre,  # tag
            filename=music_path.name,  # 文件名
            albumartist=ffprobe.format.tags.album_artist,
            language="中文",  # FIXME: detect_language
        )

    def save_with_ffmpeg(self):
        """通过ffmpeg保存信息"""

    @classmethod
    def from_mutagen(cls, music_path: str | Path):
        """通过mutagen保存信息"""
        from mutagen import File as MutagenFile

        _mu = MutagenFile(music_path)

        return cls(
            title=_mu.tags["title"],  # tag
            artist=_mu.tags.get("artist"),  # tag
            year=_mu.tags.get("year"),  # tag
            comment=_mu.tags.get("comment"),  # tag
            lyrics=_mu.tags.get("lyrics"),  # tag
            duration=_mu.info.length,  # format
            size=Path(_mu.filename).stat().st_size,  # format
            bit_rate=_mu.info.bitrate,  # format
            tracknumber=_mu.tags.get("tracknumber"),  # tag CD Track Number
            discnumber=_mu.tags.get("discnumber"),  # tag CD Disc Number
            artwork=_mu.pictures[0].data if _mu.pictures else None,  # 封面
            artwork_w=_mu.pictures[0].width if _mu.pictures else None,  # video stream
            artwork_h=_mu.pictures[0].height if _mu.pictures else None,  # video stream
            artwork_size=_mu.pictures[0].data.__len__() if _mu.pictures else None,
            album=_mu.tags.get("album"),  # tag
            album_type=_mu.tags.get("album_type"),
            genre=_mu.tags.get("genre"),
            filename=music_path.name,
            albumartist=_mu.tags.get("albumartist"),
            language="中文",  # FIXME: detect_language
        )

    def save_with_mutagen(self):
        """通过mutagen保存信息"""
        from mutagen import File as MutagenFile

        _mu = MutagenFile(self.file_full_path)
        _mu.tags.title = self.title
        _mu.tags.artist = self.artist
        _mu.tags.year = self.year
        _mu.tags.comment = self.comment
        _mu.tags.lyrics = self.lyrics
        _mu.info.length = self.duration
        _mu.info.size = self.size
        _mu.info.bitrate = self.bit_rate
        _mu.tags.tracknumber = self.tracknumber
        _mu.tags.discnumber = self.discnumber
        _mu.tags.album = self.album
        _mu.tags.album_type = self.album_type
        _mu.tags.genre = self.genre
        _mu.tags.albumartist = self.albumartist
        _mu.tags.save()


class FetchMusic(SQLModel):
    """{"prefix": "F000",
        "extra": "flac",
        "notice": "无损品质 FLAC",
        "mid": "001YVo3U4H3LLH",
        "musicid": 320315208,
        "id": "001YVo3U4H3LLH",
        "size": "25.64MB",
        "name": "时光洪流",
        "artist": "程响",
        "album": "时光洪流",
        "album_id": "0028W4QN0xB85F",
        "year": "2021-08-17",
        "readableText": "2021-08-17 程响 - 时光洪流 | 无损品质 FLAC",
        "album_img": "http://y.qq.com/music/photo_new/T002R300x300M0000028W4QN0xB85F.jpg"
    }"""

    prefix: str
    extra: str
    notice: str
    mid: str
    musicid: int
    id: str
    size: str
    name: str
    artist: str
    album: str
    album_id: str
    year: str
    readableText: str
    album_img: str


class ResponseModel(SQLModel):
    code: str = "200"
    data: None | str | list[File] | MusicId3 | list[FetchMusic] | list[
        dict
    ] | Any = None
    message: str = "success"
    result: bool = True
