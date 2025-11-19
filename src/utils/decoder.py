# file: utils/decoder.py
import re
import json
import sys
import subprocess

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
    """parse key=value pairs inside the last {}.
    """
    result = {}
    for item in block.split():
        if "=" in item:
            key, value = item.split("=", 1)
            result[key] = value
    return result

def resolve_fname(pid, fd):
    """resolve file path from pid and fd.
    """
    try:
        path = subprocess.check_output(
            ["./utils/rlink.sh", str(pid), str(fd)],
            stderr=subprocess.DEVNULL
        ).decode("utf-8").strip()

        if path:
            return path
    except:
        pass
    return "UNKNOWN"

def process_log(input_file, ref_mono, ref_wall, output_file):
    """read the input logs line by line and convert them into a jsonl
    """
    with open(input_file, "r") as infile, open(output_file, "w") as outfile:
        for line in infile:
            line = line.rstrip("\n")

            m = pattern.match(line)
            if not m:
                # not matching → print & store as-is
                print(line)
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

            # check the missing filename
            fname = kv.get("fname", "")

            if fname == "" or fname is None:
                fd = kv.get("fd")
                if fd and pid:
                    kv["fname"] = resolve_fname(pid, fd)
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


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: decoder.py <ref_mono> <ref_wall> <input> <output>")
        sys.exit(1)

    ref_mono = float(sys.argv[1])          # seconds (float)
    ref_wall = float(sys.argv[2])          # seconds (float)
    input_path = sys.argv[3]
    output_path = sys.argv[4]
    
    process_log(input_path, ref_mono, ref_wall, output_path+".jsonl")
