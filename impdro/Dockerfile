FROM python:3.9-slim

RUN pip install --no-cache-dir wheel aiogram

COPY . /app/
WORKDIR /app

CMD python main.py
STOPSIGNAL SIGINT
