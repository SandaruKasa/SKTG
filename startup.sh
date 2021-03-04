#!/bin/bash
cd "$(dirname "$0")"
#/bin/bash requirements.sh
python3 BetaLupi.py > betalupi/logs/$( date +%s).log& 2> betalupi/logs/error_$( date +%s).log
python3 ImpDro.py > impdro/logs/$( date +%s).log& 2> impdro/logs/error_$( date +%s).log
python3 Inspirobot.py > inspirobot/logs/$( date +%s).log& 2> inspirobot/logs/error_$( date +%s).log
