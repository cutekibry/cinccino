#!/usr/bin/python3

from telegram.ext import MessageFilter
import config
from utils import endl, escape, unescape, show_tg, read_message_norm, write_message_norm, reset_message

from telegram import Bot, utils, Update, Message
from telegram.ext import Updater, MessageHandler, CommandHandler, Filters, CallbackContext

from datetime import datetime, timezone

import logging
import coloredlogs
# logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
#                     level=logging.INFO)
coloredlogs.install(level=logging.INFO)


to_tg = True
message_cache = ""
image_cnt = 0
start_time = datetime.now(timezone.utc)


if config.PROXY_URL:
    bot = Bot(token=config.TG_TOKEN, request=utils.request.Request(
        proxy_url=config.PROXY_URL))
    updater = Updater(token=config.TG_TOKEN, use_context=True, request_kwargs={
        "proxy_url": config.PROXY_URL})
else:
    bot = Bot(token=config.TG_TOKEN, )
    updater = Updater(token=config.TG_TOKEN, use_context=True)


class FilterOvertime(MessageFilter):
    def filter(self, message: Message):
        return message.date >= start_time
filterOver = FilterOvertime()


def send(type_: str, msg: str) -> None:
    msg = unescape(msg)
    if to_tg:
        if type_ == "plain":
            bot.send_message(chat_id=config.TG_GROUP, text="[From QQ]" + msg)
        elif type_ == "image":
            bot.send_photo(chat_id=config.TG_GROUP,
                           photo=open(f"qq_image/{msg}", "rb"))


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


def work_photo(update: Update, context: CallbackContext) -> None:
    global message_cache, image_cnt

    work_text(update, context)

    image_cnt += 1
    cur = image_cnt  # In order to prevent async effects done to image_cnt
    photo = update.message.photo[-1]
    logging.info(f"getting photo #{image_cnt}")
    logging.info(f"{photo.width}x{photo.height}, {photo.file_size}")
    bot.get_file(photo.file_id).download(f"tg_image/{cur}")
    logging.info(f"getting photo #{image_cnt} finished")
    message_cache += f"plain {show_tg(update.message.from_user)}: [图片]{endl}"
    message_cache += f"image {cur}{endl}"


def work_qq_on(update: Update, context: CallbackContext) -> None:
    global message_cache

    message_cache += f"qq True{endl}"
    message_cache += f"plain {config.PAT_QQ_ON % update.message.from_user.full_name}{endl}"
    bot.send_message(chat_id=config.TG_GROUP, text=config.PAT_QQ_ON %
                     update.message.from_user.full_name)


def work_qq_off(update: Update, context: CallbackContext) -> None:
    global message_cache

    message_cache += f"plain {config.PAT_QQ_OFF % update.message.from_user.full_name}{endl}"
    message_cache += f"qq False{endl}"
    bot.send_message(chat_id=config.TG_GROUP, text=config.PAT_QQ_OFF %
                     update.message.from_user.full_name)


def work_tg_on(update: Update, context: CallbackContext) -> None:
    global message_cache, to_tg

    to_tg = True
    message_cache += f"tg True{endl}"
    message_cache += f"plain {config.PAT_TG_ON % update.message.from_user.full_name}{endl}"
    bot.send_message(chat_id=config.TG_GROUP, text=config.PAT_TG_ON %
                     update.message.from_user.full_name)


def work_tg_off(update: Update, context: CallbackContext) -> None:
    global message_cache, to_tg

    message_cache += f"plain {config.PAT_TG_OFF % update.message.from_user.full_name}{endl}"
    message_cache += f"tg False{endl}"
    bot.send_message(chat_id=config.TG_GROUP, text=config.PAT_TG_OFF %
                     update.message.from_user.full_name)
    to_tg = False


reset_message("tg")
reset_message("qq")

bot.send_message(chat_id=config.TG_GROUP, text=f"{config.BOT_NAME} 已启动。")

updater.dispatcher.add_handler(CommandHandler("to_qq_on", work_qq_on, filters=filterOver))
updater.dispatcher.add_handler(CommandHandler("to_qq_off", work_qq_off, filters=filterOver))
updater.dispatcher.add_handler(CommandHandler("to_tg_on", work_tg_on, filters=filterOver))
updater.dispatcher.add_handler(CommandHandler("to_tg_off", work_tg_off, filters=filterOver))
updater.dispatcher.add_handler(MessageHandler(Filters.photo & filterOver, work_photo))
updater.dispatcher.add_handler(MessageHandler(Filters.all & filterOver, work_text))

updater.job_queue.run_repeating(forward_from_qq, interval=config.BREAK_TIME)
updater.job_queue.run_repeating(forward_to_qq, interval=config.BREAK_TIME)

updater.start_polling()
updater.idle()
