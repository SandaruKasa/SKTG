#!/usr/bin/env bash

set -euxo pipefail

cd "${1}"

exec pybabel compile -d locales -D bot -f
