# file: scripts/gen_bpftrace.py

# generating bpftrace scripts

from jinja2 import Template
import json



def import_enteries(path: str) -> list:
    """import the scripts data to build scripts based on templates.
    """
    data = {}
    with open(path, "r") as file:
        data = json.load(file)
    return data

def read_to_str(path: str) -> str:
    """read a file data into a string.
    """
    try:
        data = ""
        with open(path, "r") as file:
            data = file.read()
        return data
    except:
        return ""

def read_template(path: str) -> Template:
    """read templates into jinja2 object.
    """
    return Template(open(path).read())

def save_template(path: str, out: str) -> None:
    """save the templates into files.
    """
    with open(path, "w") as file:
        file.write(out)


if __name__ == "__main__":
    # load scripts
    enteries = import_enteries("templates/bpftraces.json")

    # build scripts based on templates
    for entry in enteries:
        tmp = read_template(entry["source"])
        begin_section = read_to_str(entry["begin"])
        filter_section = read_to_str(entry["filter"])

        out = tmp.render(
            begin_section=begin_section, 
            filter=filter_section,
            file_name=entry["file_name"],
            usage_cmd=entry["usage_cmd"],
            enable_subprocess=entry["enable_subprocess"],
            subprocess=read_to_str(entry["subprocess"]),
            enable_kfuncs=entry["enable_kfuncs"]
        )
        
        save_template(entry["out"], out)
