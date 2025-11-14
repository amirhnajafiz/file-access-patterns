# BPFTrace

FLAP uses `bpftrace` at its core. There are two main entrypoints for using the tracers. The `entrypoint/trace.sh` script is the primary interface for initializing tracing. The `entrypoint/boot.sh` script is used for Kubernetes integration and accepts information such as the `Pod`, `Namespace`, and `Container`. For non-Kubernetes environments, it is recommended to use `entrypoint/trace.sh`, which also provides usage instructions.

## Supported Tracers

* Cgroup tracing
* PID tracing
* Command tracing
* Sandbox tracing

## Unit Tests

If you modify any tracing scripts in the `bpftrace` directory, make sure to run `entrypoint/units.sh` to validate your changes.
