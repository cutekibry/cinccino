#!/usr/bin/python3

import config
from utils import endl, escape, unescape, show_qq, read_message, write_message, reset_message

from pathlib import Path
import coloredlogs
import asyncio
import aiofiles
import re

from graia.broadcast import Broadcast
from graia.application import GraiaMiraiApplication, Session
from graia.application.message.chain import MessageChain
from graia.application.event.lifecycle import ApplicationLaunched
from graia.application.message.elements.internal import Plain, Image, Quote, At
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


def MsgPlain(text: str): return MessageChain.create([Plain(text)])


def MsgImageLocal(path: str): return MessageChain.create(
    [Image.fromLocalFile(path)])


async def send(type_: str, escaped_msg: str):
    try:
        msg = unescape(escaped_msg)
        app.logger.debug(f"send {type_} {msg}")
        if to_qq:
            if type_ == "plain":
                arr = set(re.findall(r"@([\S]+)", msg[1:]))
                if not arr:
                    await app.sendGroupMessage(config.QQ_GROUP, MsgPlain(msg))
                else:
                    send_user, msg = msg.split(": ", maxsplit=1)
                    data = await app.memberList(config.QQ_GROUP)
                    msg_chain = [Plain(f"{send_user}: ")]
                    for no in arr:
                        if no.isnumeric():
                            member = [x for x in data if x.id == int(no)]
                        else:
                            member = [x for x in data if x.name == no]
                        if member:
                            member = member[0]
                            msg_chain.append(At(member.id))
                            msg = msg.replace(f"@{no}", "");
                    msg_chain.append(Plain(msg))
                    msg_chain = MessageChain.create(msg_chain)
                    print(msg_chain)
                    await app.sendGroupMessage(config.QQ_GROUP, msg_chain)
                
            elif type_ == "image":
                await app.sendGroupMessage(config.QQ_GROUP, MsgImageLocal(f"tg_file/{msg}"))
    except Exception as e:
        app.logger.error(type(e), e.args)

async def forward_from_tg():
    global to_qq

    app.logger.debug("forward_from_tg on")

    while True:
        contents = await read_message("tg")
        try:
            app.logger.info("forward_from_tg checked")
            if contents:
                app.logger.info(f"from tg content: {contents}")

                for x in contents.strip().split("\n"):
                    if x:
                        try:
                            print(repr(x))
                            type_, escaped_msg = x.split(" ", maxsplit=1)
                            if type_ == "qq":
                                to_qq = (escaped_msg == "True")
                            await send(type_, escaped_msg)
                        except Exception as e:
                            app.logger.error(type(e), e.args)
        except:
            pass
        await asyncio.sleep(config.BREAK_TIME)


async def forward_to_tg():
    global message_cache

    app.logger.debug("forward_to_tg on")

    while True:
        app.logger.info("forward_to_tg checked")
        if message_cache:
            app.logger.info(f"to tg message: {message_cache}")
            await write_message("qq", message_cache)
            message_cache = ""
        await asyncio.sleep(config.BREAK_TIME)


async def add_into_message_cache(member, message: MessageChain):
    global message_cache, image_cnt

    if type(member) == str:
        member_name = escape(member)
    else:
        member_name = show_qq(member)

    if Quote in message:
        ref = await app.getMember(config.QQ_GROUP, message.getFirst(Quote).senderId)
        message_cache += f"plain {member_name} 回复 {show_qq(ref)}: {escape(message.asDisplay())}{endl}"
    else:
        message_cache += f"plain {member_name}: {escape(message.asDisplay())}{endl}"
    for img in message.get(Image):
        image_cnt += 1
        # Watch carefully here, the async might effect image_cnt but not cur!
        cur = image_cnt
        bytes = await img.http_to_bytes()
        async with aiofiles.open(f"qq_file/{cur}", "wb") as f:
            await f.write(bytes)
        message_cache += f"image {cur}{endl}"


async def bot_log(text: str):
    # bot_info = await app.getMember(config.QQ_GROUP, config.QQ_ACCOUNT)
    bot_info = "moonlight"
    return
    await add_into_message_cache(bot_info, MsgPlain(text))
    await send("plain", escape(text))


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
        await bot_log(config.PAT_QQ_ON % member.name)

    elif message.asDisplay().startswith("/to_tg_on"):
        message_cache += f"tg True{endl}"
        await bot_log(config.PAT_TG_ON % member.name)

    await add_into_message_cache(member, message)

    if message.asDisplay().startswith("/to_qq_off"):
        await bot_log(config.PAT_QQ_OFF % member.name)
        to_qq = False

    elif message.asDisplay().startswith("/to_tg_off"):
        await bot_log(config.PAT_TG_OFF % member.name)
        message_cache += f"tg False{endl}"



@bcc.receiver(ApplicationLaunched)
async def init():
    asyncio.create_task(bot_log(config.PAT_QQ_START))
    asyncio.create_task(forward_to_tg())
    asyncio.create_task(forward_from_tg())


reset_message("tg")
reset_message("qq")
app.launch_blocking()
