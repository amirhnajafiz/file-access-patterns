# File Access Patterns (FLAP)

![GitHub Tag](https://img.shields.io/github/v/tag/amirhnajafiz/file-access-patterns)
![GitHub top language](https://img.shields.io/github/languages/top/amirhnajafiz/file-access-patterns)
![Repo Note](https://img.shields.io/badge/in%20development%20process-CC1100)

eBPF based tool for tracing file access patterns. This project is under development, so please don't use it in any critical environment.

## Testing

Make sure to have `docker` installed on your system and run `make test` to run image build and end-to-end tests.

## Beta Images

The docker image is available (examples in `docker-compose.yaml`):

```
docker pull ghcr.io/amirhnajafiz/flap:v0.0.0-beta-2
```

## Operator

1. Webhook on pod creation
2. Extract the host
3. Signals the host daemon (pod uid, namespace, and container)
4. Starts tracing
5. Live exports the results
