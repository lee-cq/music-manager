#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@File Name  : test.py
@Author     : LeeCQ
@Date-Time  : 2023/12/24 13:59

"""

import musicbrainzngs

musicbrainzngs.set_useragent("music_manager", "0.1", "lee-cq@qq.com")

musicbrainzngs.get_artists_in_collection()
musicbrainzngs.search_artists()
