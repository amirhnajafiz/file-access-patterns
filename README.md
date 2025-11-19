# File Access Patterns (FLAP)

![GitHub Tag](https://img.shields.io/github/v/tag/amirhnajafiz/file-access-patterns)
![GitHub top language](https://img.shields.io/github/languages/top/amirhnajafiz/file-access-patterns)
![Repo Note](https://img.shields.io/badge/in%20development%20process-CC1100)

eBPF based tool for tracing file access patterns. This project is under development, so please don't use it in any critical environment.

## Core

FLAP uses `bpftrace` at its core.

* Cgroup tracing
* PID tracing
* Command tracing
* Sandbox tracing

## Operator

1. Webhook on pod creation/delete
2. Extract the required information (node, ns, pod, container, command)
3. Add an init container to wait on an specific directory on the host to finish
4. Creates a pod in the namespace on the target node (pod uid, namespace, and container)
5. Starts tracing
6. Terminate upon pod removal
