#!/usr/bin/env bash
cat <<'EOF'
normal line
@read[123, 4]: 987
@operation[/tmp/foo.txt]: something
@weird[abc,def]: nope
@badline []
EOF
