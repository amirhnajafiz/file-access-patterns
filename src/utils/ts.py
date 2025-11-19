# file: utils/ts.py
import datetime



def convert(mono: float, wall: float, input: float) -> datetime.datetime:
    ref_mono_ns = mono * 1e9
    ref_wall_ns = wall * 1e9

    # convert monotonic ns → wall-clock ns
    wall_ns = ref_wall_ns + (input - ref_mono_ns)

    # convert to Python datetime
    dt = datetime.datetime.fromtimestamp(wall_ns / 1e9)

    return dt
