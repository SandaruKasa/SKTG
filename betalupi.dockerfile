FROM python:3.9-slim

RUN apt update && apt install ffmpeg -y && apt clean
COPY requirements.txt .
RUN pip install --no-cache-dir wheel --upgrade pip && pip install --no-cache-dir -r requirements.txt

WORKDIR /run
CMD ["python3", "BetaLupi.py"]
STOPSIGNAL SIGHUP
