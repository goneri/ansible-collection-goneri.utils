#!/usr/bin/env python3

from pathlib import Path

import argparse
import collections
import re
import json
import yaml

parser = argparse.ArgumentParser()
parser.add_argument("snippet_dir", type=Path)
parser.add_argument("collection_dir", type=Path)
parser.add_argument("--config-file", type=Path, dest="config_file")
args = parser.parse_args()


START_LINE_re = r"^RETURN\s=\s(r|)(\"{3}|\'{3})$"


def load_return_block(module_file):
    in_return_block = ""
    return_block = []
    for l in module_file.read_text().split("\n"):
        if not in_return_block and re.match(START_LINE_re, l):
            in_return_block = re.match(START_LINE_re, l).group(2)
        elif in_return_block and l == in_return_block:
            in_return_block = ""
            break
        elif in_return_block and l.startswith("# content generated by"):
            pass
        elif in_return_block and l.startswith("# task: "):
            pass
        elif in_return_block:
            return_block.append(l)
    return return_block


def write_return_block(module_file, return_block, task_name):
    new_content = ""
    in_return_block = ""
    for l in module_file.read_text().split("\n"):
        if not in_return_block and re.match(START_LINE_re, l):
            in_return_block = re.match(START_LINE_re, l).group(2)
            new_content += l + "\n"
            new_content += "# content generated by the update_return_section callback"
            new_content += "# task: " + task_name + "\n"
            new_content += "\n".join(return_block)
        elif in_return_block and l == in_return_block:
            in_return_block = ""
            new_content += l + "\n"
        elif in_return_block:
            continue
        else:
            new_content += l + "\n"
    module_file.write_text(new_content.rstrip("\n") + "\n")


def ansible_unsafe_to_python(data):
    if isinstance(data, int):
        return int(data)
    elif isinstance(data, str):
        return str(data)
    elif isinstance(data, list):
        return [ansible_unsafe_to_python(i) for i in data]
    elif isinstance(data, dict):
        return {
            ansible_unsafe_to_python(k): ansible_unsafe_to_python(i)
            for k, i in data.items()
        }


if args.config_file:
    config = yaml.load(args.config_file.open())
else:
    config = {"keys": {}}

for task_file in args.snippet_dir.glob("*task.yaml"):
    task_content = yaml.load(task_file.open())
    module_name = [
        i for i in task_content[0].keys() if i not in ["name", "register", "until"]
    ][0].split(".")[-1]
    task_name = task_content[0]["name"]
    module_file = args.collection_dir / "plugins" / "modules" / f"{module_name}.py"
    result_file = args.snippet_dir / re.sub(
        r"\.task\.yaml$", ".result.json", task_file.name
    )
    result_content = json.load(result_file.open())
    result = {}
    for k, sample in result_content.items():
        k = str(k)
        if k.startswith("_"):
            continue
        if k in ["changed", "invocation", "attempts"]:
            continue

        if isinstance(sample, int):
            _type = "int"
        elif isinstance(sample, str):
            _type = "str"
        elif isinstance(sample, list):
            _type = "list"
        elif isinstance(sample, dict):
            _type = "dict"

        try:
            description = config["keys"][k]["description"]
        except KeyError:
            description = task_name

        result[k] = {
            "description": description,
            "returned": "On success",
            "type": _type,
            "sample": ansible_unsafe_to_python(sample),
        }

        existing_content = load_return_block(module_file)
        new_content = yaml.dump(result).split("\n")
        if len(new_content) > len(existing_content):
            print(
                f"the output of the last task is longer than the RETURN block of the module."
            )
        else:
            print(f"existing RETURN block is longer than the one collected")
            continue

        print(f"updating {module_file}'s RETURN block.")
        write_return_block(module_file, new_content, task_name)
