#!/usr/bin/env bash

set -euxo pipefail

cd "${1}"

exec pybabel extract --omit-header --input-dirs=. -o locales/bot.pot
