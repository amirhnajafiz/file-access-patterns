from jinja2 import Template
import json



def import_enteries(path: str) -> list:
    data = {}
    with open(path, "r") as file:
        data = json.load(file)
    return data

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
    enteries = import_enteries("scripts/enteries.json")

    for entry in enteries:
        tmp = read_template(entry["source"])
        begin_section = read_to_str(entry["begin"])
        filter_section = read_to_str(entry["filter"])

        out = tmp.render(
            begin_section=begin_section, 
            filter=filter_section,
            file_name=entry["file_name"],
            usage_cmd=entry["usage_cmd"],
            enable_subchild_tracing=entry["enable_subchild_tracing"]
        )
        
        save_template(entry["out"], out)
