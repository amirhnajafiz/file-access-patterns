#!/usr/bin/env sh
# file: entrypoint/units.sh

sudo ./tests/test_cgroups.sh
sudo ./tests/test_tracings.sh
sudo ./tests/test_filter.sh
