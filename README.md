# cinccino-bot（WIP）
**本项目仍在开发中，功能极其不完善，随时有破坏性更新，随时可能跑路。请不要在开发环境中使用该项目。**

（WIP）基于 [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) 以及 [mirai](https://github.com/mamoe/mirai) / [Graia Application for mirai-api-http](https://github.com/GraiaProject/Application) 开发的简单 QQ-Telegram 间转发程序。

## 支持操作
### QQ 侧
* [x] 文本
* [x] 静态图片
* [ ] 文件

### Telegram 侧
* [x] 文本
* [x] 静态图片
* [ ] 文件

## 注意事项
* Telegram：请保证你已将机器人的 Privacy Mode 关闭（使用 `/setprivacy@BotFather`）指令。

## 安装
**请务必保证你使用了 `root` 账户进行安装，否则可能会导致权限错误。如果你不是 `root`，可尝试使用 `sudo su` 进入 `root`。**

**目前已经过测试的平台为 `Ubuntu 20.04`，不保证对其他平台的支持。**

### 安装必要的东西
```bash
apt-get update
apt-get install git wget tar screen python3 python3-pip default-jre -y
```

其中 `tzdata` 可能会要你设置时区，分别输入 `6` 和 `70`（表示 `Asia/Shanghai`）即可。

### 安装
```bash
cd /tmp
wget https://github.com/PeterMX/tgs2animated/releases/download/v0.0.1/Linux.64.bit.Binary.xz
tar -Jxf Linux.64.bit.Binary.xz
cp tgs2animated /usr/bin/
```

### 安装 `mirai-console-loader`
```bash
mkdir /opt/mcl
cd /opt/mcl
wget https://github.com/iTXTech/mirai-console-loader/releases/download/v1.0.5/mcl-1.0.5.zip
unzip mcl-1.0.5.zip
rm mcl-1.0.5.zip
chmod +x mcl
./mcl --update-package net.mamoe:mirai-console --channel stable --version 2.5.0
./mcl --update-package net.mamoe:mirai-console-terminal --channel stable --version 2.5.0
./mcl --update-package net.mamoe:mirai-core-all --channel stable --version 2.5.0
./mcl --update-package net.mamoe:mirai-api-http --channel stable --type plugin --version 1.10.0
echo "exit" | ./mcl -u
```

在这之后，将 `/opt/mcl/config/net.mamoe.mirai-api-http/setting.yml` 中的 `authKey` 修改为你想要的值。

如果你不清楚 `authKey` 是什么：简单来说，`authKey` 就是沟通其他程序与 `mirai-api-http` 的密钥。你只需将其设置为任意长度的、仅有字母或数字构成的随机字符串，而不需要记住它。

最后，输入 `screen -s ./mcl` 进行登录。你可以输入 `/login <qq> <password>` 进行登录，也可以输入 `/autoLogin add <account> <password>` 配置自动登录（需要重启以生效）。

登录成功后，输入 `Ctrl+A+D` 以挂起该进程。

### 安装 `cinccino-bot`
```bash
git clone https://github.com/cutekibry/cinccino-bot.git /opt/cinccino-bot --depth=1
cd /opt/cinccino-bot
cp config-example.py config.py
pip3 install -r requirements.txt
```

接下来按照文件中的提示编辑 `config.py`，确保正确配置。**你需要保证其中的 `QQ_AUTHKEY` 与 `mirai-api-http`（`/opt/mcl/config/net.mamoe.mirai-api-http/setting.yml`）中 `authKey` 的值相同**。

然后，输入 `screen -s python3 qq.py` 以开启 QQ 侧 Bot。运行成功后，输入 `Ctrl+A+D` 以挂起该进程。

最后，输入 `screen -s python3 tg.py` 以开启 Telegram 侧 Bot。运行成功后，输入 `Ctrl+A+D` 以挂起该进程。
