#!/bin/python3

import config
import asyncio
import aiofiles
import time
import shutil

from graia.application.group import Member
from telegram import User

from pathlib import Path

endl = "\n"


def escape(string: str):
    return "" if string is None else string.replace("\n", "\\n")


def unescape(string: str):
    return "" if string is None else string.replace("\\n", "\n")


def show_qq(member:Member):
    return escape(f"{member.name}({member.id})")


def show_tg(user:User):
    return escape(f"{user.name}")


def reset_message(name: str):
    cnt = 0
    while Path(f"{name}_lock").exists():
        cnt += 1
        if cnt >= config.RESET_RETRY_TIMES:
            if config.RESET_FORCE_REMOVE:
                print(f"{name}_lock still exists after {config.RESET_RETRY_TIMES} attempt(s)")
                print("force remove.")
                Path(f"{name}_lock").unlink()
                break
            else:
                raise BlockingIOError(
                    f"{name}_lock still exists after {config.RESET_RETRY_TIMES} attempt(s)")
        time.sleep(config.RETRY_TIME)

    Path(f"{name}_lock").touch()
    if Path(f"{name}_message").exists():
        Path(f"{name}_message").unlink()
    if Path(f"{name}_image").exists():
        shutil.rmtree(f"{name}_image")
    Path(f"{name}_image").mkdir()
    Path(f"{name}_message").touch()
    Path(f"{name}_lock").unlink()


async def write_message(name: str, text: str):
    while Path(f"{name}_lock").exists():
        await asyncio.sleep(config.RETRY_TIME)

    Path(f"{name}_lock").touch()
    async with aiofiles.open(f"{name}_message", "a+", encoding="utf-8") as f:
        await f.write(text)
    Path(f"{name}_lock").unlink()


def write_message_norm(name: str, text: str):
    while Path(f"{name}_lock").exists():
        time.sleep(config.RETRY_TIME)

    Path(f"{name}_lock").touch()
    with open(f"{name}_message", "a+", encoding="utf-8") as f:
        f.write(text)
    Path(f"{name}_lock").unlink()


async def read_message(name: str):
    while Path(f"{name}_lock").exists():
        await asyncio.sleep(config.RETRY_TIME)

    Path(f"{name}_lock").touch()
    async with aiofiles.open(f"{name}_message", "r", encoding="utf-8") as f:
        result = await f.read()
    Path(f"{name}_message").unlink()
    Path(f"{name}_message").touch()
    Path(f"{name}_lock").unlink()
    return result


def read_message_norm(name: str):
    while Path(f"{name}_lock").exists():
        time.sleep(config.RETRY_TIME)

    Path(f"{name}_lock").touch()
    with open(f"{name}_message", "r", encoding="utf-8") as f:
        result = f.read()
    Path(f"{name}_message").unlink()
    Path(f"{name}_message").touch()
    Path(f"{name}_lock").unlink()
    return result

