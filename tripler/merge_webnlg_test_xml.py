#!/usr/bin/env python3
"""Merge generated per-size test XML files into a final-test benchmark file."""

from __future__ import annotations

import argparse
import copy
from pathlib import Path
from xml.etree.ElementTree import Element, ElementTree, SubElement, parse

from json_to_xml_converter import write_xml_file


def merge_test_xml(base: Path | None, generated_root: Path, output: Path) -> int:
    benchmark = Element("benchmark")
    entries = SubElement(benchmark, "entries")
    count = 0

    if base is not None:
        base_root = parse(base).getroot()
        for entry in base_root.findall("./entries/entry"):
            entries.append(copy.deepcopy(entry))
            count += 1

    generated_files = sorted(generated_root.glob("test/*triples/*.xml"))
    for generated_file in generated_files:
        generated_root_element = parse(generated_file).getroot()
        for entry in generated_root_element.findall("./entries/entry"):
            entries.append(copy.deepcopy(entry))
            count += 1

    output.parent.mkdir(parents=True, exist_ok=True)
    write_xml_file(benchmark, str(output))
    # Parse once more so a successful command guarantees a usable file.
    ElementTree(parse(output).getroot())
    return count


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generated-root", type=Path, required=True, help="Generated WebNLG en/ directory")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--base", type=Path, default=None, help="Optional existing WebNLG test XML")
    args = parser.parse_args()

    if args.base is not None and not args.base.is_file():
        parser.error(f"base XML does not exist: {args.base}")
    if not args.generated_root.is_dir():
        parser.error(f"generated root does not exist: {args.generated_root}")

    count = merge_test_xml(args.base, args.generated_root, args.output)
    print(f"merged {count} test entries into {args.output}")


if __name__ == "__main__":
    main()
