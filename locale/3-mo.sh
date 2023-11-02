#!/usr/bin/env bash

set -euxo pipefail

exec pybabel compile -d locale -D "${1}" -f
