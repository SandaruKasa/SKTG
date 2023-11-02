#!/usr/bin/env bash

set -euxo pipefail

exec pybabel update -d locale -D "${1}" -N --omit-header -i "locale/${1}.pot"
