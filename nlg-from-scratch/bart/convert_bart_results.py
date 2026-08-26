import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_JSON = Path(__file__).with_name("test.json")
DEFAULT_OUTPUTS = Path(__file__).with_name("test-normal.out")
DEFAULT_WEBNLG_TEST = (
    REPOSITORY_ROOT
    / "problems"
    / "triples_to_text"
    / "tests"
    / "webnlg"
    / "release_v3.0"
    / "en"
    / "test"
    / "rdf-to-text-generation-test-data-with-refs-en.xml"
)


PROGRAM_TEMPLATE = '''import json
from dataclasses import dataclass


@dataclass
class Triple:
    subject: str
    predicate: str
    object: str


_DATA = json.loads({data_literal})


def predict(triples: list[Triple]) -> str:
    key = json.dumps([(t.subject, t.predicate, t.object) for t in triples])
    return _DATA.get(key, "")
'''

MINIMAL_CONFIG = """evaluator:
  themis_enabled: false
  themis_name: ""
  themis_api_base: ""
  themis_api_key: ""
"""


def normalize_for_alignment(value: str) -> str:
    """Match the normalization used when loading nlg-from-scratch WebNLG data."""
    value = value.strip()
    value = value.replace("_", " ")
    value = re.sub(r'"', "", value)
    value = re.sub(r"``", "", value)
    value = re.sub(r"''", "", value)
    value = re.sub(
        r"([a-z])([A-Z])",
        lambda match: f"{match.group(1)} {match.group(2).lower()}",
        value,
    )
    return value.strip()


def parse_json_triples(value: str) -> tuple[tuple[str, str, str], ...]:
    triples = []
    for raw_triple in value.split("▸"):
        fields = tuple(field.strip() for field in raw_triple.split("|"))
        if len(fields) != 3:
            raise ValueError(f"Invalid triple: {raw_triple!r}")
        triples.append(fields)
    return tuple(triples)


def parse_xml_entries(xml_path: Path) -> list[tuple[str, tuple[tuple[str, str, str], ...]]]:
    entries = []
    for entry in ET.parse(xml_path).getroot().iter("entry"):
        triples = []
        modified_tripleset = entry.find("modifiedtripleset")
        if modified_tripleset is None:
            raise ValueError(f"Entry {entry.attrib.get('eid')} has no modifiedtripleset")

        for triple in modified_tripleset.findall("mtriple"):
            if triple.text is None:
                raise ValueError(f"Entry {entry.attrib.get('eid')} contains an empty triple")
            fields = tuple(triple.text.split(" | "))
            if len(fields) != 3:
                raise ValueError(f"Invalid XML triple in entry {entry.attrib.get('eid')}")
            triples.append(fields)

        entries.append((entry.attrib["category"], tuple(triples)))
    return entries


def make_runtime_key(
    triples: tuple[tuple[str, str, str], ...],
) -> str:
    """Build the key produced by final_test.py's Triple objects."""
    cleaned = [
        (subject.replace("_", " "), predicate, object_.replace("_", " "))
        for subject, predicate, object_ in triples
    ]
    return json.dumps(cleaned)


def validate_alignment(
    json_records: list[dict],
    output_lines: list[str],
    xml_entries: list[tuple[str, tuple[tuple[str, str, str], ...]]],
) -> None:
    if len(json_records) != len(output_lines):
        raise ValueError(
            f"Record/output count mismatch: {len(json_records)} JSON records, "
            f"{len(output_lines)} output lines"
        )
    if len(json_records) != len(xml_entries):
        raise ValueError(
            f"Record/WebNLG count mismatch: {len(json_records)} JSON records, "
            f"{len(xml_entries)} XML entries"
        )

    for index, (record, xml_entry) in enumerate(zip(json_records, xml_entries)):
        if not isinstance(record, dict) or not isinstance(record.get("in"), str):
            raise ValueError(f"JSON record {index} has no string 'in' field")

        json_triples = parse_json_triples(record["in"])
        xml_category, xml_triples = xml_entry
        normalized_json = tuple(
            tuple(normalize_for_alignment(field) for field in triple)
            for triple in json_triples
        )
        normalized_xml = tuple(
            tuple(normalize_for_alignment(field) for field in triple)
            for triple in xml_triples
        )
        if normalized_json != normalized_xml:
            raise ValueError(
                f"Input alignment failed at index {index} for XML domain "
                f"{xml_category!r}"
            )


def write_domain_program(
    domain_dir: Path,
    data: dict[str, str],
    dry_run: bool,
) -> None:
    best_dir = domain_dir / "openevolve_output" / "best"
    config_path = domain_dir / "config_remote.yaml"
    shell_path = domain_dir / f"{domain_dir.name.removesuffix('_output')}.sh"
    program_path = best_dir / "best_program.py"

    if dry_run:
        print(f"[DRY-RUN] Would create {domain_dir}")
        print(f"  {program_path.relative_to(domain_dir)} ({len(data)} entries)")
        print(f"  {config_path.name}")
        print(f"  {shell_path.name}")
        return

    best_dir.mkdir(parents=True, exist_ok=True)
    data_literal = repr(json.dumps(data, ensure_ascii=False))
    program_path.write_text(
        PROGRAM_TEMPLATE.format(data_literal=data_literal),
        encoding="utf-8",
    )
    if not config_path.exists() or config_path.stat().st_size == 0:
        config_path.write_text(MINIMAL_CONFIG, encoding="utf-8")
    if not shell_path.exists():
        shell_path.write_text("#!/bin/bash\n", encoding="utf-8")

    print(f"[WRITE] {program_path} ({len(data)} entries)")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Convert BART WebNLG outputs into domain-specific adapters usable by "
            "final_test.py."
        )
    )
    parser.add_argument(
        "--json",
        type=Path,
        default=DEFAULT_JSON,
        help=f"BART input JSON (default: {DEFAULT_JSON})",
    )
    parser.add_argument(
        "--outputs",
        type=Path,
        default=DEFAULT_OUTPUTS,
        help=f"One generated output per line (default: {DEFAULT_OUTPUTS})",
    )
    parser.add_argument(
        "--webnlg-test",
        type=Path,
        default=DEFAULT_WEBNLG_TEST,
        help=f"WebNLG test XML used by final_test.py (default: {DEFAULT_WEBNLG_TEST})",
    )
    parser.add_argument(
        "--target",
        type=Path,
        required=True,
        help="Directory in which to create <Domain>_output folders",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and report the conversion without writing files",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    json_path = args.json.resolve()
    outputs_path = args.outputs.resolve()
    webnlg_test_path = args.webnlg_test.resolve()
    target_path = args.target.resolve()

    for path in (json_path, outputs_path, webnlg_test_path):
        if not path.is_file():
            raise SystemExit(f"Input file does not exist: {path}")

    try:
        json_payload = json.loads(json_path.read_text(encoding="utf-8"))
        json_records = json_payload["data"]
        output_lines = outputs_path.read_text(encoding="utf-8").splitlines()
        xml_entries = parse_xml_entries(webnlg_test_path)
        validate_alignment(json_records, output_lines, xml_entries)
    except (KeyError, json.JSONDecodeError, ET.ParseError, ValueError) as error:
        raise SystemExit(f"Input validation failed: {error}") from error

    domain_data: dict[str, dict[str, str]] = defaultdict(dict)
    for output, (domain, xml_triples) in zip(output_lines, xml_entries):
        key = make_runtime_key(xml_triples)
        if key in domain_data[domain]:
            raise SystemExit(f"Duplicate triple key found in domain {domain!r}")
        domain_data[domain][key] = output

    print(f"Validated {len(json_records)} aligned records.")
    print(f"Found {len(domain_data)} WebNLG domains.")
    print(f"Target: {target_path}")

    if not args.dry_run:
        target_path.mkdir(parents=True, exist_ok=True)

    for domain in sorted(domain_data):
        write_domain_program(
            target_path / f"{domain}_output",
            domain_data[domain],
            dry_run=args.dry_run,
        )

    print(f"Prepared {sum(len(data) for data in domain_data.values())} outputs.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)
