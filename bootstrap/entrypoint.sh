#!/bin/sh

echo "[flap-bootstrap] Waiting for enable flag at /data/locks/<uid>/enable ..."

while true; do
    # find UID directory
    UID_DIR=$($FLAP_INIT_UID)

    if [ -z "$UID_DIR" ]; then
        echo "[flap-bootstrap] No UID directory found under /data/locks. Retrying..."
        sleep 2
        continue
    fi

    FILE="/data/locks/$UID_DIR/enable"

    if [ ! -f "$FILE" ]; then
        echo "[flap-bootstrap] Enable file not found at $FILE. Retrying..."
        sleep 2
        continue
    fi

    VALUE=$(cat "$FILE")

    if [ "$VALUE" = "0" ]; then
        echo "[flap-bootstrap] Enable file found and value = 0. Proceeding..."
        exit 0
    fi

    echo "[flap-bootstrap] Value is '$VALUE' (want 0). Retrying..."
    sleep 2
done
