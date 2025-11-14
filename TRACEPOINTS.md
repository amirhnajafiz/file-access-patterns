# Tracepoints

I/O operations:

- read
- write
- mmap
- close

File data:

- open
- openat
- dup
- dup2
- newfstat

Child processes (if not using cgroups):

- fork
- exec

## To Add

I/O operations:

- pread64
- pwrite64
- readv
- writev
- preadv
- pwritev
- munmap
- msync

File data:

- statmount
- ustat
- statx
- newlstat
- newstat
- creat
- fcntl
- newfstatat
- fstatfs
- statfs
- dup3
