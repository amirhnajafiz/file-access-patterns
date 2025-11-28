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

### Flow

```
++++++++++++++                      +++++++++++++++++
|  init container  |         ->         |  operator service  |
++++++++++++++                      +++++++++++++++++
                                                                      ||
++++++++++++++                      +++++++++++++++++
|  start target     |         <-         |  new tracer pod    |
++++++++++++++                      +++++++++++++++++
```

Init container:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: <pod>
  namespace: <ns>
  labels:
    app: k8s.io/flap-tracer
  finalizers:
    - flap-operator
spec:
  initContainers:
  - name: flap-initializer
    image: ghcr.io/amirhnajafiz/flap-init:latest
    volumeMounts:
        - name: operator-storage
          mountPath: /data
  volumes:
    - name: operator-storage
      persistentVolumeClaim:
        claimName: operator-storage
```

Tracer:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: tracer-<target>
  namespace: <ns>
  labels:
    app: k8s.io/flap-tracer
  annotations:
    target-ns: <ns>
    target-pod: <pod>
    target-container: <container>
    target-command: <command>
  finalizers:
    - flap-operator
spec:
  hostPID: true
  nodeName: <name>
  restartPolicy: Never
  securityContext:
    runAsUser: 0
  containers:
  - name: flap-core
    image: ghcr.io/amirhnajafiz/flap:latest
    command: ["python3", "/usr/local/app/entrypoint/boot.py"]
    args:
      - "-o"
    securityContext:
        privileged: true
        capabilities:
          add: ["SYS_ADMIN"]
        allowPrivilegeEscalation: true
    volumeMounts:
        - name: sysfs
          mountPath: /sys
        - name: operator-storage
          mountPath: /data
  volumes:
    - name: operator-storage
      persistentVolumeClaim:
        claimName: operator-storage
    - name: sysfs
      hostPath:
        path: /sys
        type: Directory
```
