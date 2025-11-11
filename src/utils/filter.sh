#!/usr/bin/env bash
# file: utils/filter.sh
# Usage:
#   ./filter.sh <command> [args...]

set -euo pipefail

if [ $# -eq 0 ]; then
  echo "Usage: $0 <command> [args...]"
  exit 1
fi

declare -A rlink_cache=()

# run the command and read output line by line without spawning a subshell
while IFS= read -r line || [ -n "$line" ]; do
  case "$line" in
    @*) ;;   # only process lines starting with '@'
    *) continue ;;
  esac

  # extract operation name
  if [[ "$line" =~ ^@([a-zA-Z0-9_]+)\[ ]]; then
    op="${BASH_REMATCH[1]}"
  else
    continue
  fi

  if [[ "$op" == un* ]]; then
    # match CASE A format: @op[pid, fd]: value
    if [[ "$line" =~ ^@([a-zA-Z0-9_]+)\[([0-9]+),[[:space:]]*([0-9]+)\]:[[:space:]]*(.*)$ ]]; then
      pid="${BASH_REMATCH[2]}"
      fd="${BASH_REMATCH[3]}"
      value="${BASH_REMATCH[4]}"
      key="${pid},${fd}"

      # check cache before calling rlink.sh
      if [[ -v rlink_cache[$key] ]]; then
        file="${rlink_cache[$key]}"
      else
        file="$(sudo ./utils/rlink.sh "$pid" "$fd" 2>/dev/null || echo "$pid::$fd")"
        rlink_cache[$key]="$file"
      fi

      op_no_un="${op#un_}"
      printf '@%s[%s]: %s\n' "$op_no_un" "$file" "$value"
      continue
    else
      continue
    fi
  else
    # op not starting with "un"
    if [[ "$line" =~ ^@([a-zA-Z0-9_]+)\[([^\]]+)\]:[[:space:]]*(.*)$ ]]; then
      file="${BASH_REMATCH[2]}"
      value="${BASH_REMATCH[3]}"
      printf '@%s[%s]: %s\n' "$op" "$file" "$value"
      continue
    else
      echo "$line"
    fi
  fi
done < <("$@")
