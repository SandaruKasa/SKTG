FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN ["pip", "install", "--no-cache-dir", "-r", "requirements.txt"]

RUN ["mkdir", "-m", "777", "temp"] # todo: find a better solution

COPY sktg /app/sktg
CMD ["python3", "-m", "sktg"]
