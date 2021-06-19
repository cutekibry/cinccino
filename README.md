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

## 安装
**请务必保证你使用了 `root` 账户进行安装，否则可能会导致权限错误。如果你不是 `root`，可尝试使用 `sudo su` 进入 `root`。**

**目前已经过测试的平台为 `Ubuntu 20.04`，不保证对其他平台的支持。**

### 安装必要的东西
```bash
apt-get update
apt-get install git wget screen python3 python3-pip default-jre -y
```

其中 `tzdata` 可能会要你设置时区，分别输入 `6` 和 `70`（表示 `Asia/Shanghai`）即可。

### 安装 `cinccino-bot`
```bash
git clone https://github.com/cutekibry/cinccino-bot.git /opt/cinccino-bot --depth=1
cd /opt/cinccino-bot
cp config-example.py config.py
```

接下来按照文件中的提示编辑 `config.py`，确保正确配置。

### 安装 `python3` 库
```bash
pip3 install -r requirements.txt
```

### 安装并运行 `mirai-console-loader`
```bash
mkdir /opt/mcl
cd /opt/mcl
wget https://github.com/iTXTech/mirai-console-loader/releases/download/v1.0.5/mcl-1.0.5.zip
unzip mcl-1.0.5.zip
rm mcl-1.0.5.zip
chmod +x mcl
echo "exit" | ./mcl
```

然后，安装 `mirai-api-http`：

```bash
cd /opt/mcl
./mcl --update-package net.mamoe:mirai-api-http --channel stable --type plugin
echo "exit" | ./mcl
```

在这之后，修改 `/opt/mcl/config/net.mamoe.mirai-api-http/setting.yml` 中的 `authKey`，改为与 `cinccino-bot`（`/opt/cinccino-bot/config.py`）中的值相同。

最后，输入 `screen -s ./mcl` 进行登录。你可以输入 `/login <qq> <password>` 进行登录，也可以输入 `/autoLogin add <account> <password>` 配置自动登录（需要重启以生效）。

登录成功后，输入 `Ctrl+A+D` 以挂起该进程。

### 运行 `cinccino-bot`
首先，输入 `cd /opt/cinccino-bot` 以进入 `cinccino-bot` 目录。

然后，运行 QQ 侧 Bot `screen -s python3 qq.py`。运行成功后，输入 `Ctrl+A+D` 以挂起该进程。

最后，运行 Telegram 侧 Bot `screen -s python3 tg.py`。运行成功后，输入 `Ctrl+A+D` 以挂起该进程。
