# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import collections
from pathlib import Path

import json
import os
import re
import yaml

from ansible.plugins.callback import CallbackBase


DOCUMENTATION = """
callback: collect_task_outputs
"""

IGNORED_KEYS = ["invocation", "attempts"]


class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = "aggregate"
    CALLBACK_NAME = "goneri.utils.collect_task_outputs"
    CALLBACK_NEEDS_WHITELIST = True

    def __init__(self, *args, **kwargs):
        super(CallbackModule, self).__init__(*args, **kwargs)
        self.task = None
        self.play = None

    def v2_runner_on_ok(self, result):
        r = result._result
        t = result._task

        if t.name.startswith("_"):
            return

        try:
            config = {
                "collection": os.environ["COLLECT_TASK_OUTPUTS_COLLECTION"],
                "target_dir": os.environ["COLLECT_TASK_OUTPUTS_TARGET_DIR"],
            }
        except KeyError:
            self._display.display(
                    "You must defined the following environment "
                    "variable COLLECT_TASK_OUTPUTS_COLLECTION, "
                    "COLLECT_TASK_OUTPUTS_TARGET_DIR")

        if not t.name:
            return

        collection_root_dir = (
            Path.home() / ".ansible" / "collections" / "ansible_collections"
        )
        for namespace, collection in [i.split(".") for i in t.collections]:
            if f"{namespace}.{collection}" == config["collection"]:
                self._display.display(f"The task uses {namespace}.{collection}, collecting result.")

            collection_path = collection_root_dir / namespace / collection
            module_path = collection_path / "plugins" / "modules" / (t.action + ".py")

            if not module_path.exists():
                continue
            else:
                self._display.display(f"associated module found at: {module_path}")

            target_directory = Path(config["target_dir"])
            target_directory.mkdir(exist_ok=True)
            output_task_path = target_directory / (
                t.name.replace(" ", "_") + ".task.yaml"
            )
            output_json_path = target_directory / (
                t.name.replace(" ", "_") + ".result.json"
            )

            if output_task_path.exists():
                self._display.display(f"file already exists are: {output_task_path}!!!")
                return

            play_path, line = result._task.get_path().split(":")
            play_content = Path(play_path).open().readlines()[int(line) - 1 :]
            indent_level = 0
            for i in play_content[0]:
                if i != " ":
                    break
                indent_level = +1
            task_content = play_content[0][indent_level:]
            for l in play_content[1:]:
                l = l[indent_level:]
                if not l or l.startswith("-"):
                    break
                else:
                    task_content += l
            task_result = {
                k: v
                for k, v in r.items()
                if k not in IGNORED_KEYS and not k.startswith("_")
            }
            output_task_path.write_text(task_content.rstrip("\n"))
            output_json_path.write_text(json.dumps(task_result, indent=4))
            self._display.display(f"outputs have been written")
