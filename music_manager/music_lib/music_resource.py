#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@File Name  : music_resource.py
@Author     : LeeCQ
@Date-Time  : 2023/12/23 14:58

"""
import abc
import base64
import hashlib
import json
import random
import typing
import uuid
from functools import cached_property

from httpx import AsyncClient, USE_CLIENT_DEFAULT, Response
from httpx._client import UseClientDefault
from httpx._types import (
    URLTypes,
    RequestContent,
    RequestData,
    RequestFiles,
    QueryParamTypes,
    HeaderTypes,
    CookieTypes,
    AuthTypes,
    TimeoutTypes,
    RequestExtensions,
)


class AbcClient(AsyncClient):
    """"""

    USER_AGENT_LIST = [
        (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/60.0.3112.90 Safari/537.36"
        ),
        (
            "Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) "
            "AppleWebKit/601.1.46 (KHTML, like Gecko) "
            "Version/9.0 Mobile/13B143 Safari/601.1"
        ),
        (
            "Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) "
            "AppleWebKit/601.1.46 (KHTML, like Gecko) "
            "Version/9.0 Mobile/13B143 Safari/601.1"
        ),
        (
            "Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/59.0.3071.115 Mobile Safari/537.36"
        ),
        (
            "Mozilla/5.0 (Linux; Android 6.0; "
            "Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/59.0.3071.115 Mobile Safari/537.36"
        ),
        (
            "Mozilla/5.0 (Linux; Android 5.1.1; Nexus 6 Build/LYZ28E) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/59.0.3071.115 Mobile Safari/537.36"
        ),
        (
            "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_2 like Mac OS X) "
            "AppleWebKit/603.2.4 (KHTML, like Gecko) "
            "Mobile/14F89;GameHelper"
        ),
        (
            "Mozilla/5.0 (iPhone; CPU iPhone OS 10_0 like Mac OS X) "
            "AppleWebKit/602.1.38 (KHTML, like Gecko) "
            "Version/10.0 Mobile/14A300 Safari/602.1"
        ),
        (
            "Mozilla/5.0 (iPad; CPU OS 10_0 like Mac OS X) "
            "AppleWebKit/602.1.38 (KHTML, like Gecko) "
            "Version/10.0 Mobile/14A300 Safari/602.1"
        ),
        (
            "Mozilla/5.0 (Linux; U; Android 8.1.0; zh-cn; BKK-AL10 Build/HONORBKK-AL10) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Version/4.0 Chrome/66.0.3359.126 MQQBrowser/10.6 Mobile Safari/537.36"
        ),
        (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:46.0) "
            "Gecko/20100101 Firefox/46.0"
        ),
        (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"
        ),
        (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) "
            "AppleWebKit/603.2.4 (KHTML, like Gecko) Version/10.1.1 Safari/603.2.4"
        ),
        (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:46.0) "
            "Gecko/20100101 Firefox/46.0"
        ),
        (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
        ),
        (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/42.0.2311.135 Safari/537.36 Edge/13.10586"
        ),
    ]

    @property
    def random_user_agent(self):
        return random.choice(self.USER_AGENT_LIST)

    def __init__(self):
        super().__init__()
        self.headers["User-Agent"] = self.random_user_agent
        self.timeout = 5

    async def request(self, method: str, url: URLTypes, **kwargs) -> Response:
        resp = await super().request(method, url, **kwargs)
        if resp.status_code != 200:
            raise Exception(f">> 请求失败: {resp.status_code}\n>> {resp.text}")
        return resp

    @abc.abstractmethod
    async def fetch_lyric(self, song_id):
        pass

    @abc.abstractmethod
    async def fetch_id3_by_title(self, title):
        pass


class KuwoClient(AbcClient):
    def __init__(self):
        super().__init__()
        self.headers.update(
            {
                "Referer": "http://www.kuwo.cn/",
                "Cross": self.cross,
            }
        )
        self.cookies.set("Hm_token", self.token, domain="kuwo.cn")

    @cached_property
    def token(self):
        charset = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        return "".join(random.choices(charset, k=32))

    @cached_property
    def cross(self):
        return hashlib.md5(
            hashlib.sha1(self.token.encode("utf-8")).hexdigest().encode("utf-8")
        ).hexdigest()

    async def fetch_lyric(self, song_id):
        url = f"http://kuwo.cn/newh5/singles/songinfoandlrc?musicId={song_id}"
        params = {"mid": song_id, "type": "music", "httpsStatus": 1, "plat": "web_www"}
        resp = (await self.get(url, params=params, timeout=5)).json()
        lrclist = resp.get("data", {}).get("lrclist", [])
        lyric = ""
        try:
            for line in lrclist:
                seconds = int(float(line.get("time", "0")))
                m, s = divmod(seconds, 60)
                h, m = divmod(m, 60)
                time_format = "%d:%02d:%02d" % (h, m, s)
                content = line.get("lineLyric", "")
                lyric += f"[{time_format}]{content}\n"
        except Exception as e:
            print(e)
        return lyric

    async def fetch_id3_by_title(self, title):
        url = "http://www.kuwo.cn/api/www/search/searchMusicBykeyWord"
        params = {"key": title, "pn": 1, "rn": 10, "httpsStatus": 1}
        resp = await self.get(url, params=params)
        songs = resp.json().get("data", {}).get("list", None)
        for song in songs:
            song["id"] = song["rid"]
            song["name"] = song["name"]
            song["artist"] = song["artist"]
            song["artist_id"] = song["artistid"]
            song["album"] = song["album"]
            song["album_id"] = song["albumid"]
            song["album_img"] = song["albumpic"]
            song["year"] = ""
        return songs


class MiguMusicClient(AbcClient):
    BASE_URL = "https://m.music.migu.cn/"
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0) "
        "Gecko/20100101 Firefox/80.0",
        "Referer": "https://m.music.migu.cn/",
    }

    def __init__(self):
        super().__init__()
        self.headers.update(self.header)

    async def fetch_lyric(self, song_id):
        url = (
            f"https://music.migu.cn/v3/api/"
            f"music/audioPlayer/getLyric?copyrightId={song_id}"
        )
        res = await self.get(url, headers=self.header)
        return res.json()["lyric"]

    async def fetch_id3_by_title(self, title):
        url = (
            "https://m.music.migu.cn/migu/remoting/scr_search_tag"
            f"?rows=10&type=2&keyword={title}&pgc=1"
        )
        res = await self.get(url, headers=self.header)
        songs = res.json()["musics"]
        for song in songs:
            song["id"] = song["copyrightId"]
            song["name"] = song["songName"]
            song["artist"] = song["singerName"]
            song["artist_id"] = song["singerId"]
            song["album"] = song["albumName"]
            song["album_id"] = song["albumId"]
            song["album_img"] = song["cover"]
            song["year"] = ""
        return songs


class QMusicClient(AbcClient):
    def __init__(self):
        super().__init__()
        self.headers.update(
            {
                # "User-Agent": "QQ音乐/73222 CFNetwork/1406.0.2 Darwin/22.4.0",
                "User-Agent": "QQ%E9%9F%B3%E4%B9%90/73222 CFNetwork/1406.0.3 Darwin/22.4.0",
                "Accept": "*/*",
                "Accept-Language": "zh-CN,zh-Hans;q=0.9",
                "Referer": "http://y.qq.com",
            }
        )

    async def get_music_search(self, key: str = "", page: int = 1, size: int = 15):
        url = "https://u.y.qq.com/cgi-bin/musicu.fcg"
        data = {
            "comm": {
                "wid": "",
                "tmeAppID": "qqmusic",
                "authst": "",
                "uid": "",
                "gray": "0",
                "OpenUDID": "2d484d3157d4ed482e406e6c5fdcf8c3d3275deb",
                "ct": "6",
                "patch": "2",
                "psrf_qqopenid": "",
                "sid": "",
                "psrf_access_token_expiresAt": "",
                "cv": "80600",
                "gzip": "0",
                "qq": "",
                "nettype": "2",
                "psrf_qqunionid": "",
                "psrf_qqaccess_token": "",
                "tmeLoginType": "2",
            },
            "music.search.SearchCgiService.DoSearchForQQMusicDesktop": {
                "module": "music.search.SearchCgiService",
                "method": "DoSearchForQQMusicDesktop",
                "param": {
                    "num_per_page": size,
                    "page_num": page,
                    "remoteplace": "txt.mac.search",
                    "search_type": 0,
                    "query": key,
                    "grp": 1,
                    "searchid": uuid.uuid1().__str__(),
                    "nqc_flag": 0,
                },
            },
        }
        resp = await self.post(
            url,
            content=json.dumps(data, ensure_ascii=False).encode("utf-8"),
            headers={
                "user-agent": "QQ%E9%9F%B3%E4%B9%90/73222 CFNetwork/1406.0.3 Darwin/22.4.0",
                "Accept-Encoding": "gzip, deflate",
                "Accept": "*/*",
                "Connection": "keep-alive",
                "referer": "https://y.qq.com/portal/profile.html",
                "Content-Type": "json/application;charset=utf-8",
            },
        )
        resp_data = resp.json()[
            "music.search.SearchCgiService.DoSearchForQQMusicDesktop"
        ]["data"]
        meta = resp_data["meta"]

        # 数据清洗,去掉搜索结果中多余的数据
        list_clear = [
            {
                "album": i["album"],
                "docid": i["docid"],
                "id": i["id"],
                "mid": i["mid"],
                "name": i["title"],
                "singer": i["singer"],
                "time_public": i["time_public"],
                "title": i["title"],
                "file": i["file"],
            }
            for i in resp_data["body"]["song"]["list"]
        ]

        # rebuild json
        return {
            "data": list_clear,
            "page": {
                "size": meta["sum"],  # size 搜索结果总数
                "next": meta["nextpage"],  # next 下一搜索页码 -1表示搜索结果已经到底
                "cur": meta["curpage"],  # cur  当前搜索结果页码
                "searchKey": key,
            },
        }

    @staticmethod
    def format_list(mlist):
        """处理音乐列表
        Args:
            mlist (Array<T>): 歌曲列表

        Returns:
            lists, songs: 处理过的数据数组
        """
        songs = []  # : list[Songs]
        qqmusic_song_cover = "http://y.qq.com/music/photo_new/T002R300x300M000{id}.jpg"
        mapping = {
            "size_hires": ("RS01", "flac", "高解析无损 Hi-Res"),
            "size_flac": ("F000", "flac", "无损品质 FLAC"),
            "size_320mp3": ("M800", "mp3", "超高品质 320kbps"),
            "size_192ogg": ("O600", "ogg", "高品质 OGG"),
            "size_128mp3": ("M500", "mp3", "标准品质 128kbps"),
            "size_96aac": ("C400", "m4a", "低品质 96kbps"),
        }
        for i in mlist:
            singer = ",".join([i["name"] for i in i["singer"]])
            _id = i["file"]

            # 批量下载不需要选择音质 直接开始解析为最高音质 枚举
            mid = _id["media_mid"]
            for key, value in mapping.items():
                if int(_id[key]) != 0:
                    code, _format, q_str = value
                    f_size = int(_id[key])
                    break
            else:
                code, _format, q_str, f_size = "", "", "", 0

            album_name = str(i["album"]["title"]).strip(" ") or "未分类专辑"
            readable_text = f'{i["time_public"]} {singer} - {i["title"]} | {q_str}'
            # 通过检查 将歌曲放入歌曲池展示给用户 未通过检查的歌曲将被放弃并且不再显示
            songs.append(
                {
                    "prefix": code,
                    "extra": _format,
                    "notice": q_str,
                    "mid": mid,
                    "musicid": i["id"],
                    "id": i["mid"],
                    "size": f"%.2fMB" % (f_size / 1024 / 1024),
                    "name": i["title"],
                    "artist": singer,
                    "album": album_name,
                    "album_id": i["album"]["mid"],
                    "year": i["time_public"],
                    "readableText": readable_text,
                    "album_img": qqmusic_song_cover.format(id=i["album"]["mid"]),
                }
            )
        # 这部分其实可以只返回songs 但是代码我懒得改了 反正又不是不能用=v=
        return songs

    async def fetch_lyric(self, song_id):
        resp = await self.get(
            "https://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric_new.fcg"
            "?g_tk=5381&format=json&inCharset=utf-8&outCharset=utf-8&notice=0"
            "&platform=h5&needNewCode=1&ct=121&cv=0&songmid=" + song_id
        )
        return base64.b64decode(resp.json().get("lyric", "")).decode("utf-8")

    async def fetch_id3_by_title(self, title):
        return self.format_list((await self.get_music_search(title))["data"])


class MusicResource:
    def __init__(self, info):
        self.resource = {
            "smart_tag": AbcClient,
            "netease": AbcClient,
            "migu": MiguMusicClient,
            "qmusic": QMusicClient,
            "kugou": AbcClient,
            "kuwo": KuwoClient,
            "acoustid": AbcClient,
        }[info]()

    async def fetch_lyric(self, song_id):
        try:
            return await self.resource.fetch_lyric(song_id)
        except Exception as e:
            print("音乐平台歌词获取失败", e)
            return ""

    async def fetch_id3_by_title(self, title):
        try:
            return await self.resource.fetch_id3_by_title(title)
        except Exception as e:
            print("音乐平台搜索失败", e)
            return []
