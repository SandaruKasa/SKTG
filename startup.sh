#!/bin/bash
./requirements.sh
python3 BetaLupi.py > betalupi/logs/$( date +%s).log&
python3 ImpDro.py > impdro/logs/$( date +%s).log&
python3 Inspirobot.py > inspirobot/logs/$( date +%s).log&
