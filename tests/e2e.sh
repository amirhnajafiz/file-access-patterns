#!/usr/bin/env sh

set -e

# get the script directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# rm the old logs directory if it exists
rm -rf "$SCRIPT_DIR/logs"
# create a new logs directory
mkdir -p "$SCRIPT_DIR/logs"

docker run -it \
  --privileged \
  --user root \
  --net=host \
  --pid=host \
  --ulimit memlock=-1 \
  -v /lib/modules:/lib/modules:ro \
  -v /sys/kernel/debug:/sys/kernel/debug:rw \
  -v /usr/src:/usr/src:ro \
  -v "$SCRIPT_DIR/logs":/logs:rw \
   file-access-patterns:test \
  /usr/local/app/trace.sh -c "ls" -o logs/trace_ls.txt

# display the generated log file
cat "$SCRIPT_DIR/logs/trace_ls.txt"
