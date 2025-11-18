from jinja2 import Template



ENTERIES = [
    {
        "source": "bpftrace/templates/trace.bt.j2",
        "begin": "bpftrace/templates/cgroup_trace/begin.bt",
        "filter": "bpftrace/templates/cgroup_trace/filter.bt",
        "out": "bpftrace/scripts/cgroup_trace.bt"
    }
]


def read_to_str(path: str) -> str:
    data = ""
    with open(path, "r") as file:
        data = file.read()
    return data

def read_template(path: str):
    return Template(open(path).read())

def save_template(path: str, out):
    open(path, "w").write(out)


if __name__ == "__main__":
    for entry in ENTERIES:
        tmp = read_template(entry["source"])
        begin_section = read_to_str(entry["begin"])
        filter_section = read_to_str(entry["filter"])
        out = tmp.render(begin_section=begin_section, filter=filter_section)
        save_template(entry["out"], out)
