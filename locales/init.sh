#!/usr/bin/env bash

set -euxo pipefail

cd "${1}"

for lang in ${LANGS:-en ru} ; do
    pybabel init -i locales/bot.pot -d locales -D bot -l "${lang}"
done
