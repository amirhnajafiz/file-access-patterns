#!/usr/bin/env sh
# file: utils/rlink.sh

# Usage:
#   ./rlink.sh <PID> <FD>

set -eu

# set the pid and file descriptor
pid=$1
fd=$2

# return the absolute path
sudo readlink -f "/proc/${pid}/fd/${fd}"
