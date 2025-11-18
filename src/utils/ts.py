#!/usr/bin/env python3
# file: utils/ts.py
# Usage: python3 ts.py 618549.44 1763500038.948841854 618552580474815
import sys
import datetime



def convert(mono: float, wall: float, input: float) -> datetime.datetime:
    ref_mono_ns = mono * 1e9
    ref_wall_ns = wall * 1e9

    # convert monotonic ns → wall-clock ns
    wall_ns = ref_wall_ns + (input - ref_mono_ns)

    # convert to Python datetime
    dt = datetime.datetime.fromtimestamp(wall_ns / 1e9)

    return dt


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: mono_to_date.py <ref_mono> <ref_wall> <trace_ns>")
        sys.exit(1)

    ref_mono = float(sys.argv[1])          # seconds (float)
    ref_wall = float(sys.argv[2])          # seconds (float)
    trace_ns = int(sys.argv[3])            # nanoseconds (int)

    print(convert(ref_mono, ref_wall, trace_ns).isoformat(" "))
