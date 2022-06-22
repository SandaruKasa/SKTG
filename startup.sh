#!/bin/bash
set -euxo pipefail
cd "$(dirname "$0")"

if ! which ffmpeg > /dev/null; then
	sudo apt install ffmpeg
fi

if [ ! -d venv ]; then
    python3.10 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt

python3 BetaLupi.py > betalupi/logs/$( date +%s).log& 2> betalupi/logs/error_$( date +%s).log
python3 ImpDro.py > impdro/logs/$( date +%s).log& 2> impdro/logs/error_$( date +%s).log
#python3 Inspirobot.py > inspirobot/logs/$( date +%s).log& 2> inspirobot/logs/error_$( date +%s).log
