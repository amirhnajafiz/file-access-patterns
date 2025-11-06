#!/usr/bin/env bash
# file: tests/test_cgroups.sh

./filter.sh cat <<'EOF'
normal line
@read[123, 4]: 987
@operation[/tmp/foo.txt]: something
@weird[abc,def]: nope
@badline []
EOF
