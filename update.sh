#!/usr/bin/env bash
set -euox pipefail
cd "$(dirname "$0")"

git pull
docker-compose up --build --detach
