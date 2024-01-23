#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@File Name  : model_meta.py
@Author     : LeeCQ
@Date-Time  : 2023/12/23 13:00

"""
import json
import logging
from pathlib import Path

from pydantic import BaseModel, Field, AliasChoices

from music_manager.music_lib.music_operator import runner

__all__ = [
    "BaseModel",
    "Tags",
    "FormatModel",
    "StreamsModel",
    "FfprobrModel",
]


class Tags(BaseModel):
    """
    ffprobe -v quiet -print_format json -show_format -show_streams
    """

    album: str | None = Field(None, validation_alias=AliasChoices("album", "ALBUM"))
    album_type: str | None = Field(
        None, validation_alias=AliasChoices("album_type", "ALBUM_TYPE")
    )

    album_artist: str | None = Field(
        None, validation_alias=AliasChoices("album_artist", "ALBUM_ARTIST")
    )
    artist: str | None = Field(None, validation_alias=AliasChoices("artist", "ARTIST"))
    comment: str | None = Field(
        None, validation_alias=AliasChoices("comment", "COMMENT")
    )
    composer: str | None = Field(
        None, validation_alias=AliasChoices("composer", "COMPOSER")
    )
    disc: str | None = Field(None, validation_alias=AliasChoices("disc", "DISC"))
    genre: str | None = Field(None, validation_alias=AliasChoices("genre", "GENRE"))
    lyrics: str | None = Field(None, validation_alias=AliasChoices("lyrics", "LYRICS"))
    title: str | None = Field(None, validation_alias=AliasChoices("title", "TITLE"))
    track: str | None = Field(None, validation_alias=AliasChoices("track", "TRACK"))
    year: str | None = Field(None, validation_alias=AliasChoices("year", "YEAR"))


class FormatModel(BaseModel):
    """
    ffprobe -v quiet -print_format json -show_format -show_streams
    """

    filename: str
    nb_streams: int
    nb_programs: int
    format_name: str
    format_long_name: str
    start_time: float
    duration: float
    size: int
    bit_rate: int
    probe_score: int
    tags: Tags


class StreamsModel(BaseModel):
    """
    ffprobe -v quiet -print_format json -show_format -show_streams
    """

    index: int
    profile: str | None = None  # Video Only
    codec_name: str
    codec_long_name: str
    codec_type: str
    codec_tag_string: str
    codec_tag: str
    sample_fmt: str | None = None  # Audio Only
    sample_rate: int | None = None  # Audio Only
    channels: int | None = None  # Audio Only
    channel_layout: str | None = None  # Audio Only
    bits_per_sample: int | None = None  # Audio Only
    width: int | None = None  # Video Only
    height: int | None = None  # Video Only
    coded_width: int | None = None  # Video Only
    coded_height: int | None = None  # Video Only
    has_b_frames: int | None = None  # Video Only
    sample_aspect_ratio: str | None = None  # Video Only
    display_aspect_ratio: str | None = None  # Video Only
    pix_fmt: str | None = None  # Video Only
    level: int | None = None  # Video Only
    color_range: str | None = None  # Video Only
    color_space: str | None = None  # Video Only
    color_transfer: str | None = None  # Video Only
    color_primaries: str | None = None  # Video Only
    chroma_location: str | None = None  # Video Only
    field_order: str | None = None  # Video Only
    timecode: str | None = None  # Video Only
    refs: int | None = None  # Video Only
    r_frame_rate: str | None = None  # Video Only
    avg_frame_rate: str | None = None  # Video Only
    time_base: str | None = None  # Video Only
    start_pts: int | None = None  # Video Only
    start_time: str | None = None  # Video Only
    duration_ts: int | None = None  # Video Only
    duration: str | None = None  # Audio Only
    bit_rate: str | None = None  # Audio Only
    max_bit_rate: str | None = None  # Audio Only
    bits_per_raw_sample: str | None = None  # Audio Only
    nb_frames: str | None = None  # Audio Only
    tags: Tags | None = None


class FfprobrModel(BaseModel):
    """
    ffprobe -v quiet -print_format json -show_format -show_streams
    """

    format: FormatModel
    streams: list[StreamsModel]

    def __str__(self):
        return f"{self.format.filename} {self.format.duration} {self.format.size}"

    def __repr__(self):
        return f"{self.format.filename} {self.format.duration} {self.format.size}"

    @property
    def stream_video(self) -> list[StreamsModel]:
        return [_ for _ in self.streams if _.codec_type == "video"]

    @property
    def stream_audio(self) -> list[StreamsModel]:
        return [_ for _ in self.streams if _.codec_type == "audio"]

    @classmethod
    def from_meta(cls, meta: dict):
        return cls(**meta)

    @classmethod
    def from_media_file(cls, file_path: str | Path):
        """
        获取音乐文件的元数据
        :param file_path: 音乐文件路径
        :return:
        """
        cmd = [
            f"ffprobe",
            "-v",
            "quiet",
            "-print_format",
            "json",
            "-show_format",
            "-show_streams",
            # "-show_entries",
            file_path,
        ]
        stdout, stderr = runner(cmd)
        return cls.from_meta(json.loads(stdout.decode("utf-8")))


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    ff = FfprobrModel.from_media_file("/Users/lcq/Music/KwMusic/flac/Beyond-海阔天空.flac")
    print(ff)
    print(ff.stream_video)
    print(ff.stream_audio)
