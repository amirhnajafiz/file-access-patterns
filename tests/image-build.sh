#!/usr/bin/env sh

set -e

docker build -t file-access-patterns:test -f build/Dockerfile src/
docker run --user root --rm file-access-patterns:test /usr/local/app/trace.sh -h
