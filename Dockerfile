FROM python:3.10-slim AS junior

ENV DATABASE_FILE=/var/db/db.sqlite3
VOLUME /var/db

ENV TMP_DIR=/tmp

WORKDIR /usr/src

COPY junior/requirements.txt requirements.txt
RUN ["pip", "install", "--no-cache-dir", "-r", "requirements.txt"]

COPY junior junior

RUN pybabel compile -d junior/locales -D bot -f

CMD ["python3", "-m", "junior"]
STOPSIGNAL SIGINT


FROM python:3.11-alpine AS spinbot

RUN pip install --no-cache-dir "aiogram~=3.1"
COPY spinbot.py ./

CMD ["python3", "spinbot.py"]
STOPSIGNAL SIGINT
