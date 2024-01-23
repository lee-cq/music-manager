#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@File Name  : __main__.py
@Author     : LeeCQ
@Date-Time  : 2023/12/29 19:56

"""
from pathlib import Path

import rich
import typer

from music_manager.config import music_library, data_dir


app = typer.Typer(name="music manager")


@app.command(name="init")
def init():
    """初始化"""
    typer.echo("Initializing music_manager...")
    music_library.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)

    from music_manager.music_lib.database import init as init_db

    init_db()

    typer.echo("[green]music_manager initialized![/green]")


@app.command(name="import")
def imports(path: Path = typer.Argument(help="需要导入的音乐文件或包含音乐文件的目录")):
    """导入音乐文件或目录"""
    from music_manager.music_lib.importer import import_music

    res = import_music(path)
    rich.print(res)


if __name__ == "__main__":
    app()
