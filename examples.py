#!/usr/bin/env python3

"""examples/*.py driven README + pytest generator

While there is plenty of state of the art for both, having one small
script is better than two different dedicated tools.

"""

import re
from enum import Enum
from pathlib import Path

README_PATH = Path(__file__).parent.absolute() / "README.md"
README_TMP_PATH = Path(__file__).parent.absolute() / "README.md.tmp"
EXAMPLE_DIR = Path(__file__).parent.absolute() / "examples"


class UpdateState(Enum):
    WAITING_COMMENT = 0
    WAITING_BLOCK = 1
    WAITING_BLOCK_END = 2


def update_readme() -> bool:
    example2text = {}
    for example_path in EXAMPLE_DIR.glob("*.py"):
        example2text[example_path.name] = example_path.read_text()

    old_text = README_PATH.read_text()
    lines = []
    state = UpdateState.WAITING_COMMENT
    comment_match = re.compile(r"^{::comment}examples/(\S+){:/comment}\s*$").match
    example = ""
    for line in old_text.split("\n"):
        line = line.rstrip()
        if state == UpdateState.WAITING_COMMENT:
            m = comment_match(line)
            if m is not None:
                example = example2text[m.group(1)]
                state = UpdateState.WAITING_BLOCK
        elif state == UpdateState.WAITING_BLOCK and line == "```python":
            lines.append(line)
            lines.extend([line.rstrip() for line in example.split("\n")])
            state = UpdateState.WAITING_BLOCK_END
            continue
        elif state == UpdateState.WAITING_BLOCK_END:
            if line != "```":
                # Omit the previous version of the example
                continue
            state = UpdateState.WAITING_COMMENT
        lines.append(line)
    new_text = "\n".join(lines)
    if old_text == new_text:
        return True
    README_TMP_PATH.write_text(new_text)
    README_TMP_PATH.replace(README_PATH)
    return False


def generate_pytest() -> None:
    # This produces Python which doesn't quite handle our coding
    # style, but we have Ruff for that
    print("""# Automatically generated pytest definition, please do not edit

import pytest
from root import RootSignals
""")
    skip_line_match = re.compile(r"^(\s*#.*|from root import RootSignals|\s*)$").match
    for example_path in EXAMPLE_DIR.glob("*.py"):
        print("")
        print(f"def test_{example_path.stem}():")
        for line in example_path.read_text().split("\n"):
            line = line.rstrip()
            if skip_line_match(line) is not None:
                continue
            print("", line)


if __name__ == "__main__":
    import argparse
    import sys

    p = argparse.ArgumentParser(description="Example handler")
    p.add_argument(
        "--update-readme",
        "-g",
        action="store_true",
        help="Update README.md with contents of examples; if it changes, return an error",
    )
    p.add_argument(
        "--generate-pytest", "-t", action="store_true", help="Generate test module with contents of examples"
    )
    args = p.parse_args()
    if args.update_readme:
        if not update_readme():
            sys.exit(1)
    if args.generate_pytest:
        generate_pytest()
