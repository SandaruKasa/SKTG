#!/usr/bin/env bash

set -euxo pipefail

exec pybabel extract --omit-header --input-dirs="${1}" -o "locale/${1}.pot"
