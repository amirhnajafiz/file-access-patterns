#!/usr/bin/env sh

# ./e2e.sh
# runs an end-to-end test to validate the program
# functionality.

set -e

# get the script directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Running end-to-end test for file-access-patterns..."
echo "Logs will be stored in $SCRIPT_DIR/logs, and will be removed after the test."

# rm the old logs directory if it exists
rm -rf "$SCRIPT_DIR/logs"
# create a new logs directory
mkdir -p "$SCRIPT_DIR/logs"

# need a privileged container with root access to run tracer program.
# also need to use the hosts tracepoints.
docker run -it \
  --privileged \
  --user root \
  --net=host \
  --pid=host \
  --ulimit memlock=-1 \
  -v /lib/modules:/lib/modules:ro \
  -v /sys/kernel/debug:/sys/kernel/debug:rw \
  -v "$SCRIPT_DIR/logs":/logs:rw \
   file-access-patterns:test \
  /usr/local/app/entrypoint/trace.sh -c "ls" -o /logs/trace_ls.txt

# display the generated log file
cat "$SCRIPT_DIR/logs/trace_ls.txt"

# remove the logs directory after the test
rm -rf "$SCRIPT_DIR/logs"
