FROM python:3.10-slim AS base

ENV DATABASE_FILE=/var/db/db.sqlite3
VOLUME /var/db

ENV TMP_DIR=/tmp

WORKDIR /usr/src

STOPSIGNAL SIGINT


FROM base as junior

COPY junior/requirements.txt requirements.txt
RUN ["pip", "install", "--no-cache-dir", "-r", "requirements.txt"]

COPY util util
COPY junior junior

RUN pybabel compile -d junior/locales -D bot -f

CMD ["python3", "-m", "junior"]


FROM python:3.11-alpine AS spinbot

RUN pip install --no-cache-dir "aiogram~=3.1"
COPY spinbot.py ./

CMD ["python3", "spinbot.py"]
STOPSIGNAL SIGINT
