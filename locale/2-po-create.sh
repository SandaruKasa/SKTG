#!/usr/bin/env bash

set -euxo pipefail

for lang in ${LANGS:-en ru} ; do
    pybabel init -i "locale/${1}.pot" -d locale -D "${1}" -l "${lang}"
done
