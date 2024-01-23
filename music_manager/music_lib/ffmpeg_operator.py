#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@File Name  : ffmpeg_operator.py
@Author     : LeeCQ
@Date-Time  : 2023/12/22 23:57

"""
import json
import logging
import os
import subprocess
from pathlib import Path
from typing import List

logger = logging.getLogger("task.music_operator")


def fund_exec(file_name: str, file_path: str | Path = "") -> Path:
    """
    获取文件的绝对路径
    :param file_path:
    :param file_name:
    :return:
    """
    if os.name == "nt":
        file_name = file_name + ".exe"

    if file_path:
        file_path = Path(file_path)
        file_path = (
            file_path if file_path.name == file_name else file_path.joinpath(file_name)
        )
        if file_path.exists():
            return file_path
        raise FileNotFoundError(f"文件不存在: {file_path} not in {file_path} ")

    paths = set(os.getenv("PATH").split(":"))
    paths.add(os.getcwd())
    paths.add(Path.home().joinpath("bin"))
    paths.add(Path.home().joinpath(".local/bin"))
    for path in paths:
        file_path = Path(path).joinpath(file_name)
        if file_path.exists():
            return file_path

    raise FileNotFoundError(f"文件不存在: {file_name} not in {paths}[{os.getenv('SHELL')}]")


def runner(cmd: list[str] | str) -> tuple[bytes, bytes]:
    """
    执行命令
    :param cmd:
    :return:
    """
    if isinstance(cmd, list):
        cmd[0] = fund_exec(cmd[0]) if isinstance(cmd[0], str) else cmd[0]
    logger.debug("CMD: %s", " ".join(str(_) for _ in cmd))
    res = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = res.communicate()
    if res.returncode != 0:
        raise RuntimeError(stderr.decode())
    return stdout, stderr


def get_music_meta(file_path: str | Path) -> dict:
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
        f"-show_format",
        "-show_streams",
        file_path,
    ]
    stdout, stderr = runner(cmd)
    return json.loads(stdout.decode("utf-8"))


def get_music_artwork(file_path: str | Path) -> bytes:
    """
    获取音乐文件的封面
    :param file_path: 音乐文件路径
    :return:
    """
    cmd = [
        "ffmpeg",
        "-i",
        file_path,
        "-an",
        "-vcodec",
        "copy",
        "-f",
        "image2pipe",
        "-",
    ]
    stdout, stderr = runner(cmd)
    return stdout


if __name__ == "__main__":
    import json

    print(
        json.dumps(
            get_music_meta("/Users/lcq/Music/KwMusic/flac/Beyond-海阔天空.flac"),
            indent=4,
            ensure_ascii=False,
        ),
        file=open("Beyond-海阔天空.json", "w"),
    )
    # open("Beyond-海阔天空.jpg", "wb").write(
    #     get_music_artwork()
    # )
    # print(Path.cwd())
