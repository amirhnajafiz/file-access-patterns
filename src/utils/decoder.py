# file: utils/decoder.py
import re
import json
import subprocess
import argparse

from ts import convert



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
                outfile.write(line + "\n")
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

            fname = kv.get("fname", "")
            if not fname:
                fd = kv.get("fd")
                if fd and pid:
                    kv["fname"] = resolve_fname(pid, fd, fname_cache)
                else:
                    kv["fname"] = "UNKNOWN"
            
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
    parser = argparse.ArgumentParser(description="Decode and reformat trace logs.")
    parser.add_argument("--ref_mono", type=float, required=True, help="Reference monotonic base time (float seconds).")
    parser.add_argument("--ref_wall", type=float, required=True, help="Reference wallclock base time (float seconds).")
    parser.add_argument("--input", type=str, required=True, help="Input log file path.")
    parser.add_argument("--output", type=str, required=True, help="Output JSONL file path.")
    args = parser.parse_args()
    
    process_log(args.input, args.ref_mono, args.ref_wall, args.output)

if __name__ == "__main__":
    main()
