# 使用python镜像自定义我们的镜像
FROM python:3.8-slim AS build

# 时区同步
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8 PYTHONUNBUFFERED=1
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

#创建/app目录
RUN mkdir /app

#将项目文件内的requirements.txt拷贝到/app
COPY ./requirements.txt /app
#COPY ./setup.py /app
COPY ./app /app

#使用国内163源
ADD sources.list /etc/apt

#切换到/app目录
WORKDIR /app

#使用豆瓣源https://pypi.douban.com/simple安装项目的python依赖
RUN python3 -m pip install --upgrade pip && pip3 install -r requirements.txt --trusted-host https://pypi.douban.com/simple -i https://pypi.douban.com/simple

RUN apt-get autoremove &&\
    apt-get autoclean

FROM build AS builder

#将内部的8019端口暴露出去
EXPOSE 8019

ENV PYTHONPATH "${PYTHONPATH}:/app:/app/api:/app/utils"

#使用uvicorn启动应用，IP为0.0.0.0，端口为8019（这里的端口是8019，那么EXPOSE暴露的端口也必须是这个）
CMD ["uvicorn","main:app","--host","0.0.0.0","--port","8019","--reload"]

