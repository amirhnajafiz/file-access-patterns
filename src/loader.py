#!/usr/bin/env python3
# file: loader.py

import argparse
import logging



def main(pod: str, ns: str, container: str) -> None:
    logging.info(
        "Monitoring Container: {} for Pod: {} in Namespace: {}".format(
        container,
        pod,
        ns,
    ))

    while True:
        break

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
