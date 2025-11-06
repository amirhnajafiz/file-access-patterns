#!/usr/bin/env bash
# file: tests/test_cgroups.sh

./filter.sh cat <<'EOF'
noise line
@un_read[123, 4]: 987
@read[file]: 987
@write[fileB]: 10
@un_write[111, 2]: 1
EOF
