import datetime

ref_mono = 618549.44
ref_wall = 1763500038.948841854
ref_mono_ns = ref_mono * 1e9
ref_wall_ns = ref_wall * 1e9

def mono_to_datetime(mono_ns):
    wall_ns = ref_wall_ns + (mono_ns - ref_mono_ns)
    return datetime.datetime.fromtimestamp(wall_ns / 1e9)

# Example trace entry:
trace_ns = 618552580474815  # sample from bpftrace

print(mono_to_datetime(trace_ns))
