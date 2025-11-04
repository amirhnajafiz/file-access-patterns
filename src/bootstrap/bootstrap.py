#!/usr/bin/env python3
# file: bootstrap.py

import argparse
import logging
import sys
import time
from cri import get_cid_by_name



def main(pod: str, ns: str, container: str) -> None:
    logging.info(
        "Monitoring Container: {} for Pod: {} in Namespace: {}".format(
            container,
            pod,
            ns,
        )
    )

    while True:
        cid, err = get_cid_by_name(container=container, pod=pod, ns=ns)
        if cid is None:
            logging.warning(
                "get cid failed: {}".format(
                    err
                )
            )
        else:
            print(cid)
            # run the tracer: ./trace.sh -cg cid -o /tmp/logs.txt
            sys.exit(0)
        
        time.sleep(0.5)

if __name__ == "__main__":
    # set the logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # create an arg parser
    parser = argparse.ArgumentParser()

    parser.add_argument("-p", "--pod", type=str, help="Specify the target pod name.", required=True)
    parser.add_argument("-n", "--namespace", type=str, help="Specify the target namespace.", required=True)
    parser.add_argument("-c", "--container", type=str, help="Specify the target container name.", required=True)

    # parse the flags into an args variable
    args = parser.parse_args()

    main(pod=args.pod, ns=args.namespace, container=args.container)
