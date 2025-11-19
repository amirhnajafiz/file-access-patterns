# file: utils/decoder.py
import argparse
import datetime
import re
import json
import os
import subprocess



# regex for your pattern
pattern = re.compile(
    r"""^\s*
    (?P<timestamp>\d+)\s+
    \{\s*pid=(?P<pid>\d+)\s+tid=(?P<tid>\d+)\s+proc=(?P<proc>[^\s]+)\s*\}\s+
    \{\s*(?P<etype>ENTER|EXIT)\s+(?P<operand>[^\s]+)\s*\}\s+
    \{\s*(?P<kv>.*?)\s*\}
    """,
    re.VERBOSE,
)

def convert(mono: float, wall: float, input: float) -> datetime.datetime:
    """convert nanosecond to datetime."""
    ref_mono_ns = mono * 1e9
    ref_wall_ns = wall * 1e9

    # convert monotonic ns → wall-clock ns
    wall_ns = ref_wall_ns + (input - ref_mono_ns)

    # convert to Python datetime
    dt = datetime.datetime.fromtimestamp(wall_ns / 1e9)

    return dt

def parse_kv(block):
    """parse key=value pairs inside the last {}."""
    result = {}
    for item in block.split():
        if "=" in item:
            key, value = item.split("=", 1)
            result[key] = value
    return result

def resolve_fname(pid, fd, cache):
    """resolve file path from pid and fd, using a cache dict keyed by (pid, fd)."""
    key = (pid, fd)
    if key in cache:
        return cache[key]
    try:
        path = subprocess.check_output(
            ["./utils/rlink.sh", str(pid), str(fd)],
            stderr=subprocess.DEVNULL
        ).decode("utf-8").strip()
        if path:
            cache[key] = path
            return path
    except Exception as e:
        print(f"resolve_fname failed: {e}")
    cache[key] = "UNKNOWN"
    return "UNKNOWN"

def process_log(input_file, ref_mono, ref_wall, output_file):
    """read the input logs line by line and convert them into a jsonl"""
    fname_cache = {}
    with open(input_file, "r") as infile, open(output_file, "w") as outfile:
        for line in infile:
            line = line.rstrip("\n")

            m = pattern.match(line)
            if not m:
                continue
            
            # extract matched components
            timestamp = int(m.group("timestamp"))
            pid = int(m.group("pid"))
            tid = int(m.group("tid"))
            proc = m.group("proc")
            etype = m.group("etype")
            operand = m.group("operand")
            kv_raw = m.group("kv")

            kv = parse_kv(kv_raw)

            fd = kv.get("fd")
            if fd and pid:
                kv["rfname"] = resolve_fname(pid, fd, fname_cache)
            else:
                kv["rfname"] = "UNKNOWN"
            
            # construct structured data for saving
            parsed = {
                "timestamp": convert(ref_mono, ref_wall, timestamp).isoformat(" "),
                "pid": pid,
                "tid": tid,
                "proc": proc,
                "event_type": etype,
                "operand": operand,
                "details": kv,
            }

            outfile.write(json.dumps(parsed) + "\n")

def main():
    parser = argparse.ArgumentParser(description="Decode and reformat trace logs from a directory.")
    parser.add_argument("--dir", type=str, default="logs", required=False, help="Input directory containing meta.json and logs.txt.")
    args = parser.parse_args()

    input_dir = args.dir
    meta_path = os.path.join(input_dir, "meta.json")
    input_path = os.path.join(input_dir, "logs.txt")
    output_path = os.path.join(input_dir, "logs.jsonl")

    with open(meta_path, "r") as meta_file:
        meta = json.load(meta_file)
        ref_mono = float(meta['ref_mono'])
        ref_wall = float(meta['ref_wall'])

    process_log(input_path, ref_mono, ref_wall, output_path)

if __name__ == "__main__":
    main()
