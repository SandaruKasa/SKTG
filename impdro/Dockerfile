FROM python:3.9-slim

RUN pip install --no-cache-dir wheel "aiogram~=2.25"

COPY . /app/
WORKDIR /app

CMD ["python3", "main.py"]
STOPSIGNAL SIGINT
