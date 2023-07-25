FROM python:3.9-slim

RUN apt update && apt install ffmpeg -y && apt clean
RUN pip install --no-cache-dir wheel --upgrade pip && pip install --no-cache-dir requests "pillow<10" pydub

WORKDIR /run
CMD ["python3", "BetaLupi.py"]
STOPSIGNAL SIGHUP
