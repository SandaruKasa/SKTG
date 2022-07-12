FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN ["pip", "install", "--no-cache-dir", "-r", "requirements.txt"]

ENV DATABASE_FILE=/var/db/db.sqlite3
VOLUME /var/db

ENV TMP_DIR=/tmp

COPY sktg /app/sktg
CMD ["python3", "-m", "sktg"]
STOPSIGNAL SIGINT
