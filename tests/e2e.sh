#!/usr/bin/env sh

set -e

docker run -it \
  --privileged \
  --user root \
  --net=host \
  --pid=host \
  --ulimit memlock=-1 \
  -v /lib/modules:/lib/modules:ro \
  -v /sys/kernel/debug:/sys/kernel/debug:rw \
  -v /usr/src:/usr/src:ro \
  -v "$(pwd)/logs":/logs:rw \
   file-access-patterns:test \
  /usr/local/app/trace.sh -c "ls" -o logs
