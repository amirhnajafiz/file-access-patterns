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

# Set the working directory
WORKDIR /usr/local/app

# Copy the files into the working directory
COPY src/ .

# Set executable permissions for the trace script
RUN chmod +x /usr/local/app/entrypoint/trace.sh && chmod +x /usr/local/app/entrypoint/boot.sh

# Default command
CMD ["/bin/sh"]
