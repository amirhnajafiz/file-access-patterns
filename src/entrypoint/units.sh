#!/usr/bin/env sh
# file: entrypoint/units.sh

./tests/test_cgroups.sh
./tests/test_tracings.sh
./tests/test_filter.sh
