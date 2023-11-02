FROM python:3.11-alpine

ENV DATABASE_FILE=/var/db/db.sqlite3
VOLUME /var/db

ENV TMP_DIR=/tmp

WORKDIR /usr/src

COPY requirements.txt .
RUN ["pip", "install", "--no-cache-dir", "wheel", "-r", "requirements.txt"]

COPY junior junior

RUN pybabel compile -d junior/locales -D bot -f

CMD ["python3", "-m", "junior"]
STOPSIGNAL SIGINT
