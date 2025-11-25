# file: scripts/gen_bpftrace.py
# generating bpftrace scripts by reading the j2 files in `templates` directory.

from jinja2 import Template
import json
import os



CONFIG_PATH = "templates/tracers.json"


def import_json(path: str) -> dict:
    """import json data into a dictionary.
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
    # load the configs
    cfg = import_json(CONFIG_PATH)

    print(f"loading {CONFIG_PATH} ...")

    # form the template paths
    templates_dir_path = os.path.join(cfg["templates_dir"], cfg["sources_dir"])

    # generate bpftrace scripts by going through inputs and sources
    for entry in cfg["inputs"]:
        # form the paths
        dir_path = os.path.join(cfg["templates_dir"], cfg["inputs_dir"], entry)
        filter_path = os.path.join(dir_path, "filter.bt")
        begin_path = os.path.join(dir_path, "begin.bt")
        output_dir_path = os.path.join(cfg["outputs_dir"], entry)

        os.makedirs(output_dir_path, exist_ok=True)

        # read inputs
        filter_section = read_to_str(filter_path)
        begin_section = read_to_str(begin_path)

        # create the outputs
        for out in cfg["sources"]:
            # form the paths
            template_path = os.path.join(templates_dir_path, out) + ".j2"
            output_path = os.path.join(output_dir_path, out)

            tmp = read_template(template_path)

            res = tmp.render(
                begin_section=begin_section,
                filter=filter_section
            )
        
            save_template(output_path , res)

    print("scripts generated successfully.")
