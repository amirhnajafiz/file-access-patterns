#!/usr/bin/env sh

# ./image-build.sh
# this script builds a temporary docker image to test
# the program.

set -e

docker build -t file-access-patterns:test -f build/Dockerfile .

# user must be root since the tracing program runs privileged syscalls
docker run --user root --rm file-access-patterns:test /usr/local/app/trace.sh -h

