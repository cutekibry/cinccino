#!/usr/bin/python3

from PIL import Image
import coloredlogs
import logging
import config
from utils import endl, escape, unescape, show_tg, read_message_norm, write_message_norm, reset_message, get_mimetype


from telegram import Bot, utils, Update, Message
from telegram.ext import Updater, MessageFilter, MessageHandler, CommandHandler, Filters, CallbackContext


from datetime import datetime, timezone
start_time = datetime.now(timezone.utc)
from os import system


coloredlogs.install(level=logging.DEBUG if config.DEBUG else logging.INFO)


to_tg = True
message_cache = ""
file_cnt = 0


if config.PROXY_URL:
    bot = Bot(token=config.TG_TOKEN, request=utils.request.Request(
        proxy_url=config.PROXY_URL))
    updater = Updater(token=config.TG_TOKEN, use_context=True, request_kwargs={
        "proxy_url": config.PROXY_URL})
else:
    bot = Bot(token=config.TG_TOKEN)
    updater = Updater(token=config.TG_TOKEN, use_context=True)


class FilterOvertime(MessageFilter):
    def filter(self, message: Message):
        return message.date >= start_time and message.chat.id == int(config.TG_GROUP)


filterOver = FilterOvertime()


def send(type_: str, msg: str) -> None:
    msg = unescape(msg)
    if to_tg:
        if type_ == "plain":
            bot.send_message(chat_id=config.TG_GROUP, text=msg)
        elif type_ == "image":
            bot.send_photo(chat_id=config.TG_GROUP,
                           photo=open(f"qq_file/{msg}", "rb"))


def bot_log(text: str) -> None:
    global message_cache

    message_cache += f"plain {show_tg(bot.get_me())}: {escape(text)}{endl}"
    bot.send_message(chat_id=config.TG_GROUP, text=text)


def forward_from_qq(context: CallbackContext) -> None:
    global to_tg

    contents = read_message_norm("qq")
    if contents:
        logging.info(f"from qq content: {contents}")
        for x in contents.strip().split("\n"):
            if x:
                print(repr(x))
                type_, msg = x.split(" ", maxsplit=1)
                if type_ == "tg":
                    to_tg = (msg == "True")
                send(type_, msg)


def forward_to_qq(context: CallbackContext) -> None:
    global message_cache

    if message_cache:
        logging.info(f"to qq message: {message_cache}")
        write_message_norm("tg", message_cache)
        message_cache = ""


def work_text(update: Update, context: CallbackContext) -> None:
    global message_cache

    m = update.message

    logging.info(f"{show_tg(m.from_user)}: {escape(m.text)}")

    if m.text is not None:
        if m.reply_to_message is not None:
            message_cache += f"plain {show_tg(m.from_user)} 回复 {show_tg(m.reply_to_message.from_user)}: {escape(m.text)}{endl}"
        else:
            message_cache += f"plain {show_tg(m.from_user)}: {escape(m.text)}{endl}"


def work_image(update: Update, context: CallbackContext) -> None:
    global message_cache, file_cnt

    logging.info("get image")

    content = update.message.effective_attachment
    if isinstance(content, list):
        content = content[-1]

    file_cnt += 1
    cur = file_cnt  # In order to prevent async effects done to image_cnt
    bot.get_file(content.file_id).download(f"tg_file/{cur}")

    print(get_mimetype(f"tg_file/{cur}"))
    if get_mimetype(f"tg_file/{cur}") == "application/gzip":
        logging.info("open tgs2animated")
        system(f"tgs2animated -i tg_file/{cur} -o tg_file/{cur}")
    if get_mimetype(f"tg_file/{cur}") == "image/webp":
        img = Image.open(f"tg_file/{cur}")
        img.save(f"tg_file/{cur}", format="png")
        img.close()

    message_cache += f"plain {show_tg(update.message.from_user)}: [图片]{endl}"
    message_cache += f"image {cur}{endl}"


def work_qq_on(update: Update, context: CallbackContext) -> None:
    global message_cache

    message_cache += f"qq True{endl}"
    bot_log(config.PAT_QQ_ON % show_tg(update.message.from_user))


def work_qq_off(update: Update, context: CallbackContext) -> None:
    global message_cache

    bot_log(config.PAT_QQ_OFF % show_tg(update.message.from_user))
    message_cache += f"qq False{endl}"


def work_tg_on(update: Update, context: CallbackContext) -> None:
    global to_tg

    to_tg = True
    bot_log(config.PAT_TG_ON % show_tg(update.message.from_user))


def work_tg_off(update: Update, context: CallbackContext) -> None:
    global to_tg

    bot_log(config.PAT_TG_OFF % show_tg(update.message.from_user))
    to_tg = False


reset_message("tg")
reset_message("qq")

bot_log(config.PAT_TG_START)

updater.dispatcher.add_handler(CommandHandler(
    "to_qq_on", work_qq_on, filters=filterOver))
updater.dispatcher.add_handler(CommandHandler(
    "to_qq_off", work_qq_off, filters=filterOver))
updater.dispatcher.add_handler(CommandHandler(
    "to_tg_on", work_tg_on, filters=filterOver))
updater.dispatcher.add_handler(CommandHandler(
    "to_tg_off", work_tg_off, filters=filterOver))
updater.dispatcher.add_handler(MessageHandler(
    (Filters.photo | Filters.sticker | Filters.animation) & filterOver, work_image))
updater.dispatcher.add_handler(
    MessageHandler(Filters.all & filterOver, work_text))

updater.job_queue.run_repeating(forward_from_qq, interval=config.BREAK_TIME)
updater.job_queue.run_repeating(forward_to_qq, interval=config.BREAK_TIME)

updater.start_polling()
updater.idle()
