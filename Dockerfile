FROM python:3.11-alpine as sktg

STOPSIGNAL SIGINT

ENV DATABASE_FILE=/var/db/db.sqlite3
VOLUME /var/db

ENV TMP_DIR=/tmp

WORKDIR /run

COPY sktg/requirements.txt .
RUN ["pip", "install", "--no-cache-dir", "wheel", "-r", "requirements.txt"]
COPY sktg sktg


FROM sktg AS junior

COPY junior/requirements.txt .
RUN ["pip", "install", "--no-cache-dir", "wheel", "-r", "requirements.txt"]
COPY junior junior

COPY locale locale
RUN pybabel compile -d locale -D junior -f

CMD ["python3", "-m", "junior"]
