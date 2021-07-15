# 机器人显示名称，可以随意更改
BOT_NAME = "bot"


# `mirai-api-http` 使用的 `authKey`，是一个仅由字母或数字组成的字符串
# 对于不了解 `authKey` 的用户：简单来说，`AuthKey` 就是沟通其他程序与 `mirai-api-http` 的密钥
# 安全起见，请务必更改该变量
# 如果你还是不能明白，把它更改为随便某个随机串就行了
QQ_AUTHKEY = "INITKEYoshawott"
# QQ 号
QQ_ACCOUNT = 2054986856
# QQ 群群号
QQ_GROUP = 707408530


# 从 @BotFather 得到的 Token，形如 1234567890:BUTWs9b8w75hBWOGH20shw0gh2WwGwwg9a
TG_TOKEN = "1818115281:AAF5LQ2e1uP6KSezXn9cilOp3LgbCSgvCZs"
# Telegram 群群号，注意要用字符串形式储存且开头必须为减号（`-`）
# 可以将 @GroupIDbot 拉入群并输入 `/id@GroupIDbot` 获得该群群号
TG_GROUP = "-556374837"


# 如果你需要设置 Telegram 代理的话请填写，否则使用空选项
PROXY_URL = ""  # 无代理
# PROXY_URL = "socks5://127.0.0.1:1089/"  # socks5 代理
# PROXY_URL = "http://127.0.0.1:8889/"  # http 代理


# 是否开启调试信息
DEBUG = False


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# 警告：若你不清楚下列参数的意义，最好不要随意更改下列参数
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# 读取 / 写入文件的间隔时间，简单来说就是「转发间隔时间」
BREAK_TIME = 1

# 当读取文件上锁时的休息时间、重试最大次数，以及超过最大次数时是否要强行删除锁
# 运行程序退出时可能没有删除锁，导致锁一直存在
RETRY_TIME = 0.1
RESET_RETRY_TIMES = 50
RESET_FORCE_REMOVE = True


# 一些模式串，更改了也没什么用
PAT_QQ_START = f"QQ 侧转发机器人已开启。"
PAT_TG_START = f"Telegram 侧转发机器人已开启。"
PAT_QQ_ON = f"Telegram 至 QQ 的转发被 %s 开启了。"
PAT_QQ_OFF = f"Telegram 至 QQ 的转发被 %s 关闭了。"
PAT_TG_ON = f"QQ 至 Telegram 的转发被 %s 开启了。"
PAT_TG_OFF = f"QQ 至 Telegram 的转发被 %s 关闭了。"
