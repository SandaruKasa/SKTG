FROM python:3.11-alpine

COPY requirements.txt .
RUN ["pip", "install", "--no-cache-dir", "wheel", "-r", "requirements.txt"]
COPY spinbot.py .

CMD ["python3", "spinbot.py"]
STOPSIGNAL SIGINT
