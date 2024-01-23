#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@File Name  : test_task_resource.py
@Author     : LeeCQ
@Date-Time  : 2023/12/23 15:46

"""
import asyncio

import pytest

from music_resource import KuwoClient, MiguMusicClient, QMusicClient


@pytest.mark.skip(reason="逆向失败")
class TestKuwoClient:
    def test_lrc(self):
        client = KuwoClient()
        res = client.fetch_lyric("123")
        print(res)
        assert res == "123"

    def test_search(self):
        client = KuwoClient()
        res = asyncio.run(client.fetch_id3_by_title("莉莉安"))
        print(res)
        assert res == "123"


@pytest.mark.parametrize(
    "client, title, song_id",
    [
        (MiguMusicClient, "莉莉安", "6903170C6SZ"),
        (QMusicClient, "时光洪流", "001YVo3U4H3LLH"),
    ],
)
class TestClient:
    # def __init__(self, client, title, expect):
    #     self.client = client
    #     self.title = title
    #     self.song_id = expect

    def test_lrc(self, client, title, song_id):
        client = client()
        res = asyncio.run(client.fetch_lyric(song_id))
        print(res)

    def test_search(self, client, title, song_id):
        client = client()
        res = asyncio.run(client.fetch_id3_by_title(title))
        print(res)
        assert isinstance(res, list)


def test_():
    client = MiguMusicClient()
    res = asyncio.run(client.fetch_id3_by_title("时光洪流"))
    print(res)
    assert isinstance(res, list)
