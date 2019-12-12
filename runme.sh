#!/usr/bin/env bash

MODULE="${1:-client}"
ARG="$2"
PORT="${3:-4000}"

docker build -t pycat docker
docker run -it --rm --name "pycat-$PORT" -p "$PORT:4000" -v `pwd`:/home/pycat/pycat -e MODULE="$MODULE" -e ARG="$ARG" pycat
