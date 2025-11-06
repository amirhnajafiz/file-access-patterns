#!/usr/bin/env bash
# file: utils/filter.sh

# Usage:
#   ./filter.sh <command> [args...]

set -eu

if [ $# -eq 0 ]; then
  echo "Usage: $0 <command> [args...]"
  exit 1
fi

# run the command and read output line by line
"$@" | while IFS= read -r line; do
  # process only lines that start with @
  [[ "$line" != @* ]] && continue

  # case 1: @operation[file]: value
  if [[ "$line" =~ ^@([a-zA-Z0-9_]+)\[([^\],]+)\]:[[:space:]]*(.*)$ ]]; then
    op="${BASH_REMATCH[1]}"
    file="${BASH_REMATCH[2]}"
    value="${BASH_REMATCH[3]}"
    echo "@${op}[${file}]: ${value}"
    continue
  fi

  # case 2: @un_operation[pid, fd]: value
  if [[ "$line" =~ ^@([a-zA-Z0-9_]+)\[([0-9]+),[[:space:]]*([0-9]+)\]:[[:space:]]*(.*)$ ]]; then
    op="${BASH_REMATCH[1]}"
    pid="${BASH_REMATCH[2]}"
    fd="${BASH_REMATCH[3]}"
    value="${BASH_REMATCH[4]}"

    # call rlink.sh to resolve pid+fd => filename
    file="$(sudo ./utils/rlink.sh "$pid" "$fd" 2>/dev/null || echo "unknown")"

    echo "@${op}[${file}]: ${value}"
    continue
  fi

done
