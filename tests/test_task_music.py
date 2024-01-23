#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@File Name  : test_task_music.py
@Author     : LeeCQ
@Date-Time  : 2023/12/23 13:19

"""
import json
from pathlib import Path

import pytest

from music_models import *

models_json = Path(__file__).parent.joinpath("models_json")


@pytest.mark.parametrize(
    "tag_json",
    json.load(models_json.joinpath("task_music_tags.json").open(encoding="utf-8")),
)
def test_tags_model(tag_json):
    model: Tags = Tags(**tag_json)
    assert isinstance(model.album, str | None)


@pytest.mark.parametrize(
    "format_json",
    json.load(models_json.joinpath("task_music_formats.json").open(encoding="utf-8")),
)
def test_format_model(format_json):
    model = FormatModel(**format_json)
    assert isinstance(model.size, int)
    assert isinstance(model.tags, Tags)


@pytest.mark.parametrize(
    "stream_json",
    json.load(models_json.joinpath("task_music_streams.json").open(encoding="utf-8")),
)
def test_stream_model(stream_json):
    model = StreamsModel(**stream_json)
    assert model.codec_type in ("audio", "video", "subtitle")
