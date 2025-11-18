#!/usr/bin/env sh
# file: start.sh

# Usage: ./start session-name pid_ns

SESSION="flap-$1"
OUTPUT_DIR="/tmp/lttng-traces/${SESSION}"
PIDNS="$2"

# create a new session
lttng create "${SESSION}" --output "${OUTPUT_DIR}"

# create session's channels
lttng enable-channel --session="${SESSION}" --kernel --subbuf-size=30M chan1
lttng enable-channel --session="${SESSION}" --kernel --subbuf-size=30M chan2

# enable system-call events
lttng enable-event --session="${SESSION}" --kernel --syscall --channel=chan1 \
    read,write,pread64,pwrite64,readv,writev,preadv,pwritev,mmap \
    --filter="\$ctx.pid_ns == ${PIDNS}"

# enable kprobes events
lttng enable-event --session="${SESSION}" --kernel --channel=chan2 \
    block_rq_complete,block_rq_issue,mm_page_free,mm_page_alloc,kmem_mm_page_alloc,kmem_mm_page_free \
    --filter="\$ctx.pid_ns == ${PIDNS}"

# enable context options
lttng add-context --session="${SESSION}" --kernel \
    --type pid \
    --type procname \
    --type pid_ns

# start the tracer
lttng start "${SESSION}"
