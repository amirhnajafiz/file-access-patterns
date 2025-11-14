#!/usr/bin/env sh
# file: entrypoint/units.sh

set -u

tests=(
    ./tests/test_cgroups.sh
    ./tests/test_tracings.sh
    ./tests/test_filter.sh
)

for t in "${tests[@]}"; do
    echo "Running $t..."
    if ! "$t"; then
        echo "❌ ERROR: $t failed!" >&2
        exit 1
    fi
done

echo "✔ All tests passed."
