#!/usr/bin/env sh
# file: entrypoint/units.sh

run_test() {
    script="$1"
    echo "Running $script..."

    "$script"
    rc=$?

    if [ "$rc" -ne 0 ]; then
        echo "ERROR: $script failed with exit code $rc" >&2
        exit 1
    fi
}

run_test ./tests/test_cgroups.sh
run_test ./tests/test_tracings.sh
run_test ./tests/test_filter.sh

echo "All tests passed."
