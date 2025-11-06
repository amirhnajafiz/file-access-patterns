#!/usr/bin/env bash
# file: filter.sh
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
  case "$line" in
    @*) ;;   # only process lines starting with '@'
    *) continue ;;
  esac

  # extract operation name at minimum to decide
  if [[ "$line" =~ ^@([a-zA-Z0-9_]+)\[ ]]; then
    op="${BASH_REMATCH[1]}"
  else
    # no recognizable pattern — skip
    continue
  fi

  # if op starts with "un" => resolve pid,fd => filename
  if [[ "$op" == un* ]]; then
    # match CASE A format: @op[pid, fd]: value
    if [[ "$line" =~ ^@([a-zA-Z0-9_]+)\[([0-9]+),[[:space:]]*([0-9]+)\]:[[:space:]]*(.*)$ ]]; then
      pid="${BASH_REMATCH[2]}"
      fd="${BASH_REMATCH[3]}"
      value="${BASH_REMATCH[4]}"
      # get filename via utils/rlink.sh
      file="$(sudo ./utils/rlink.sh "$pid" "$fd" 2>/dev/null || echo "$pid::$fd")"
      # remove "un_" prefix before printing
      op_no_un="${op#un_}"
      printf '@%s[%s]: %s\n' "$op_no_un" "$file" "$value"
      continue
    else
      # unmatched, optional: print or skip
      continue
    fi
  else
    # op not starting with "un", just print line (could directly print or verify CASE B)
    if [[ "$line" =~ ^@([a-zA-Z0-9_]+)\[([^\]]+)\]:[[:space:]]*(.*)$ ]]; then
      file="${BASH_REMATCH[2]}"
      value="${BASH_REMATCH[3]}"
      printf '@%s[%s]: %s\n' "$op" "$file" "$value"
      continue
    else
      # fallback: raw print line or ignore
      echo "$line"
    fi
  fi
done < <("$@")
