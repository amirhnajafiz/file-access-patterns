# file: cri.py

import json
import subprocess



def get_cid_by_name(container: str, ns: str, pod: str) -> tuple[str, str]:
    """Find the container id by it's namespace and pod name

    @param
        container: container name
        ns: namespace
        pod: pod name
    @returns
        str: container id
    """
    resp = subprocess.run([
        "crictl",
        "ps",
        "--namespace",
        ns,
        "--pod",
        pod,
        "--output",
        "json"
    ])
    if resp.returncode != 0:
        return (None, resp.stderr)

    try:
        data = json.loads(resp.stdout)
        containers = data["containers"]
        for c in containers:
            if c["metadata"]["name"] == container:
                return (c["id"], "")
    except Exception as e:
        return (None, e)

    return (None, "container not found!")
