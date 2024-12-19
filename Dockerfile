FROM ubuntu:22.04

# 安裝環境
RUN apt-get update && apt-get install -y \
    build-essential \
    g++ \
    make \
    python3 \
    python3-pip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --upgrade pip &&\
    pip install fastapi jinja2 uvicorn docker python-multipart
RUN apt-get update && apt-get install vim -y


WORKDIR /app
COPY . .

EXPOSE $PORT
CMD uvicorn main:app --host 0.0.0.0 --post $PORT
