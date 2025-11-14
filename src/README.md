# BPFTrace

FLAP uses `bpftrace` at its core. There are two main entrypoints to use tracers. The `entrypoint/trace.sh` is the main script to initialize a tracing. The `entrypoint/boot.sh` is for Kubernetes integration that accepts information such as `Pod`, `Namespace`, and `Container`. For non-Kubernetes usage, it is suggested to use the `entrypoint/trace.sh` which provides usage instructions too.

## Unit Tests

If you ever want to modify the tracing scripts in `bpftrace` directory, make sure to run `entrypoint/units.sh` to validate your changes.
