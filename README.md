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

## TODO

- [ ] List of required mount points
- [ ] List of requried capabilities needed for the main process
- [ ] Separate pipeline for beta images
- [ ] K8S Operator to update manifests upon pod creation using annotations/labels
- [ ] Live monitoring (exporting the results as Prometheus metrics)
