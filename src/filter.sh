#!/usr/bin/env bash
# file: utils/filter.sh
# Usage:
#   ./filter.sh <command> [args...]

set -euo pipefail

if [ $# -eq 0 ]; then
  echo "Usage: $0 <command> [args...]"
  exit 1
fi

# run the command and read output line by line without spawning a subshell
# (requires bash for process substitution)
while IFS= read -r line || [ -n "$line" ]; do
  # process only lines that start with '@'
  case "$line" in
    @*) ;;   # ok, continue processing
    *) continue ;;
  esac

  # CASE A: @op[pid, fd]: value   (numeric pid,fd)  -> resolve filename via rlink.sh
  if [[ "$line" =~ ^@([a-zA-Z0-9_]+)\[([0-9]+),[[:space:]]*([0-9]+)\]:[[:space:]]*(.*)$ ]]; then
    op="${BASH_REMATCH[1]}"
    pid="${BASH_REMATCH[2]}"
    fd="${BASH_REMATCH[3]}"
    value="${BASH_REMATCH[4]}"

    # call rlink.sh to resolve pid+fd => filename; fallback to "unknown" on error
    # remove `sudo` here if you prefer calling script without prompting for password
    file="$(sudo ./rlink.sh "$pid" "$fd" 2>/dev/null || echo "unknown")"

    printf '@%s[%s]: %s\n' "$op" "$file" "$value"
    continue
  fi

  # CASE B: @op[file]: value   (generic file-name or other bracket content)
  if [[ "$line" =~ ^@([a-zA-Z0-9_]+)\[([^\]]+)\]:[[:space:]]*(.*)$ ]]; then
    op="${BASH_REMATCH[1]}"
    file="${BASH_REMATCH[2]}"
    value="${BASH_REMATCH[3]}"
    printf '@%s[%s]: %s\n' "$op" "$file" "$value"
    continue
  fi

  # If it started with @ but didn't match patterns, optionally print or ignore:
  # echo "unrecognized: $line" >&2
done < <("$@")
