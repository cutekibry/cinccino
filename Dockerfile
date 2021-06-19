# Java: 11.0.11

# iTXTech Mirai Console Loader: 1.0.5
# mirai-console: 2.6.7
# mirai-console-terminal: 2.6.7
# mirai-core-all: 2.6.7

FROM ubuntu

ENV LANG C.UTF-8

# 6/70 denotes "Asia/Shanghai" for tzdata in openjdk-11-jdk
RUN echo -e "6\n70\n" | \
    apt-get update && apt-get install \
    wget \
    screen \
    python3 \
    python3-pip \
    default-jre \
    -y

RUN pip3 install \
    python-telegram-bot \
    graia-application-mirai \
    aiofiles \
    pydantic==1.7.1 \
    coloredlogs \
    pysocks

RUN echo Installing iTXTech MCL \
    && cd /opt \
    && mkdir mcl \
    && wget https://github.com/iTXTech/mirai-console-loader/releases/download/v1.0.5/mcl-1.0.5.zip \
    && unzip mcl-1.0.5.zip \
    && rm mcl-1.0.5.zip \
    && chmod +x mcl \
    && echo "exit" | ./mcl

RUN echo Installing mirai-api-http \
    && ./mcl --update-package net.mamoe:mirai-api-http --channel stable --type plugin \
    && echo "exit" | ./mcl 
COPY config/mirai-api-http.yml /opt/mcl/config/net.mamoe.mirai-api-http/setting.yml
RUN screen -s ./mcl

COPY bot /opt/bot/