# Use official Ubuntu 24.04 as base image
FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# Install ebpf (bpftrace) dependencies
RUN apt-get update && apt-get install -y \
    bpftrace \
    linux-tools-generic \
    linux-tools-common \
    linux-headers-generic \
    libbpf-dev \
    llvm \
    clang \
    iproute2 \
    git \
    ca-certificates \
    make \
    g++ \
    kmod \
    wget \
    curl \
    xz-utils \
    procps \
    strace \
    && rm -rf /var/lib/apt/lists/*

# Default command
CMD ["/bin/sh"]
