#!/usr/bin/env bash

set -euxo pipefail

bash "$(dirname "${0}")"/extract.sh "${@}"

cd "${1}"
exec pybabel update -d locales -D bot -N --omit-header -i locales/bot.pot
