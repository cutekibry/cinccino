#!/usr/bin/python3

import config
from utils import endl, escape, unescape, show_qq, read_message, write_message, reset_message

from pathlib import Path
import coloredlogs

from graia.broadcast import Broadcast
from graia.application import GraiaMiraiApplication, Session
from graia.application.message.chain import MessageChain
from graia.application.event.lifecycle import ApplicationLaunched
import asyncio
import aiofiles

from graia.application.message.elements.internal import Plain, Image, Quote
from graia.application.friend import Friend
from graia.application.group import Group, Member

loop = asyncio.get_event_loop()

bcc = Broadcast(loop=loop)
app = GraiaMiraiApplication(
    broadcast=bcc,
    connect_info=Session(
        host="http://localhost:8080",  # 填入 httpapi 服务运行的地址
        authKey=config.QQ_AUTHKEY,  # 填入 authKey
        account=config.QQ_ACCOUNT,  # 你的机器人的 qq 号
        websocket=True  # Graia 已经可以根据所配置的消息接收的方式来保证消息接收部分的正常运作.
    ),
    debug=config.DEBUG
)

coloredlogs.install(level='DEBUG' if config.DEBUG else 'INFO')

to_qq = True

qq_group = app.getGroup(config.QQ_GROUP)
message_cache = ""
image_cnt = 0

if qq_group is None:
    raise RuntimeError(
        f"The QQ Group (id = {config.QQ_GROUP}) can't be gathered.")


async def send(type_: str, msg: str):
    global qq_group
    msg = unescape(msg)
    app.logger.debug(f"send {type_} {msg}")
    if to_qq:
        if type_ == "plain":
            await app.sendGroupMessage(config.QQ_GROUP, MessageChain.create([Plain(msg)]))
        elif type_ == "image":
            await app.sendGroupMessage(config.QQ_GROUP, MessageChain.create([Image.fromLocalFile(f"tg_image/{msg}")]))


async def forward_from_tg():
    global to_qq

    app.logger.debug("forward_from_tg on")

    while True:
        contents = await read_message("tg")

        app.logger.debug("forward_from_tg checked")
        if contents:
            app.logger.info(f"from tg content: {contents}")

            for x in contents.strip().split("\n"):
                if x:
                    print(repr(x))
                    type_, msg = x.split(" ", maxsplit=1)
                    if type_ == "qq":
                        to_qq = (msg == "True")
                    await send(type_, msg)
        await asyncio.sleep(config.BREAK_TIME)


async def forward_to_tg():
    global message_cache

    app.logger.debug("forward_to_tg on")

    while True:
        app.logger.debug("forward_to_tg checked")
        if message_cache:
            app.logger.info(f"to tg message: {message_cache}")
            await write_message("qq", message_cache)
            message_cache = ""
        await asyncio.sleep(config.BREAK_TIME)


async def work_msg(member, message: MessageChain):
    global message_cache, image_cnt

    if Quote in message:
        ref = await app.getMember(config.QQ_GROUP, message.getFirst(Quote).senderId)
        message_cache += f"plain {show_qq(member)} 回复 {show_qq(ref)}: {escape(message.asDisplay())}{endl}"
    else:
        message_cache += f"plain {show_qq(member)}: {escape(message.asDisplay())}{endl}"
    for img in message.get(Image):
        image_cnt += 1
        # Watch carefully here, the async might effect image_cnt but not cur!
        cur = image_cnt
        bytes = await img.http_to_bytes()
        async with aiofiles.open(f"qq_image/{cur}", "wb") as f:
            await f.write(bytes)
        message_cache += f"image {cur}{endl}"


@bcc.receiver("FriendMessage")
async def friend_message_listener(app: GraiaMiraiApplication, friend: Friend):
    await app.sendFriendMessage(friend, MessageChain.create([
        Plain("Hello, World!")
    ]))
    if friend.id == 2054986856:
        await app.sendGroupMessage(config.QQ_GROUP, MessageChain.create([Plain("test")]))


@bcc.receiver("GroupMessage")
async def group_message_handler(
    message: MessageChain,
    app: GraiaMiraiApplication,
    group: Group, member: Member,
):
    global qq_group, to_qq, message_cache

    if group.id != config.QQ_GROUP or member.id == config.QQ_ACCOUNT:
        return

    if message.asDisplay().startswith("/to_qq_on"):
        to_qq = True
        message_cache += f"qq True{endl}"

        await send("plain", config.PAT_QQ_ON % member.name)
        work_msg({"name": config.BOT_NAME}, MessageChain.create(
            [Plain(config.PAT_QQ_ON % member.name)]))

    elif message.asDisplay().startswith("/to_qq_off"):
        await send("plain", config.PAT_QQ_OFF % member.name)
        work_msg({"name": config.BOT_NAME}, MessageChain.create(
            [Plain(config.PAT_QQ_OFF % member.name)]))

        to_qq = False
        message_cache += f"qq False{endl}"

    elif message.asDisplay().startswith("/to_tg_on"):
        message_cache += f"tg True{endl}"

        await send("plain", config.PAT_TG_ON % member.name)
        work_msg({"name": config.BOT_NAME}, MessageChain.create(
            [Plain(config.PAT_TG_ON % member.name)]))

    elif message.asDisplay().startswith("/to_tg_off"):
        await send("plain", config.PAT_TG_OFF % member.name)
        work_msg({"name": config.BOT_NAME}, MessageChain.create(
            [Plain(config.PAT_TG_OFF % member.name)]))

        message_cache += f"tg False{endl}"

    await work_msg(member, message)


@bcc.receiver(ApplicationLaunched)
async def init():
    asyncio.create_task(forward_to_tg())
    asyncio.create_task(forward_from_tg())


reset_message("tg")
reset_message("qq")
app.launch_blocking()
