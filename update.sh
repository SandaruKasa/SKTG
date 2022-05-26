#!/usr/bin/env bash
set -euox pipefail
cd "$(dirname "$0")"

git pull
DOCKER_UID=$(id -u) DOCKER_GID=$(id -g) docker-compose up --build --detach
