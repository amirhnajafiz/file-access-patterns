#!/usr/bin/env sh
# file: start.sh

# Usage: ./start session-name cgroup

SESSION="flap-$1"
OUTPUT_DIR="/tmp/lttng-traces/${SESSION}"
CGROUP="$2"

# create a new session
lttng create "${SESSION}" --output "${OUTPUT_DIR}"

# create session's channels
lttng enable-channel --session="${SESSION}" --kernel --subbuf-size=30M chan1
lttng enable-channel --session="${SESSION}" --kernel --subbuf-size=30M chan2

# enable system-call events
lttng enable-event --session="${SESSION}" --kernel --syscall --channel=chan1 \
    read,write,pread64,pwrite64,readv,writev,preadv,pwritev,mmap \

# enable kprobes events
lttng enable-event --session="${SESSION}" --kernel --channel=chan2 \
    block_rq_complete,block_rq_issue,mm_page_free,mm_page_alloc,kmem_mm_page_alloc,kmem_mm_page_free \

# enable context options
lttng add-context --session="${SESSION}" --kernel \
    --type pid \
    --type tid \
    --type ppid \
    --type procname \
    --type vpid \
    --type vtid \
    --type cgroup_ns

# start the tracer
lttng start "${SESSION}"
