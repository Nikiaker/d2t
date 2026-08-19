import argparse
import os
import sys
from pathlib import Path

import dill


WRAPPER_TEMPLATE = '''from dataclasses import dataclass

@dataclass
class Triple:
    subject: str
    predicate: str
    object: str

{program_code}

def predict(triples: list[Triple]) -> str:
    system = NLGSystem()
    return system.verbalize_set_of_triples(triples)
'''


def convert_checkpoint(checkpoint_path: Path, target_root: Path) -> bool:
    if not checkpoint_path.name.startswith("chpt-"):
        return False

    domain = checkpoint_path.name.removeprefix("chpt-")
    print(f"Processing {domain}...")

    try:
        with open(checkpoint_path, "rb") as f:
            program = dill.load(f)
            curr_iteration = dill.load(f)
            best_program = dill.load(f)
            best_num_successes_test = dill.load(f)
    except Exception as e:
        print(f"  ERROR loading checkpoint: {e}")
        return False

    if not isinstance(best_program, str):
        print(f"  ERROR: best_program is not a string, got {type(best_program)}")
        return False

    if "NLGSystem" not in best_program or "verbalize_set_of_triples" not in best_program:
        print(f"  ERROR: best_program does not contain expected NLGSystem class")
        return False

    target_dir = target_root / f"{domain}_output"
    best_dir = target_dir / "openevolve_output" / "best"
    best_dir.mkdir(parents=True, exist_ok=True)

    wrapped_code = WRAPPER_TEMPLATE.format(program_code=best_program)
    best_program_path = best_dir / "best_program.py"
    with open(best_program_path, "w", encoding="utf-8") as f:
        f.write(wrapped_code)
    print(f"  Written: {best_program_path}")

    config_path = target_dir / "config_remote.yaml"
    config_path.touch()
    print(f"  Created: {config_path}")

    sh_path = target_dir / f"{domain}.sh"
    sh_path.write_text("#!/bin/bash\n")
    print(f"  Created: {sh_path}")

    print(f"  Stats: iteration={curr_iteration}, best_successes={best_num_successes_test}")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Convert nlg-from-scratch checkpoint files to zeroshot output structure."
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=Path(__file__).parent / "chpt-programs" / "webnlg" / "llama",
        help="Directory containing chpt-<Domain> checkpoint files",
    )
    parser.add_argument(
        "--target",
        type=Path,
        required=True,
        help="Target directory for <Domain>_output folders",
    )
    args = parser.parse_args()

    source_dir = args.source.resolve()
    target_dir = args.target.resolve()

    if not source_dir.exists():
        print(f"ERROR: Source directory does not exist: {source_dir}", file=sys.stderr)
        sys.exit(1)

    checkpoint_files = sorted([f for f in source_dir.iterdir() if f.is_file() and f.name.startswith("chpt-")])

    if not checkpoint_files:
        print(f"No checkpoint files found in {source_dir}")
        sys.exit(0)

    print(f"Found {len(checkpoint_files)} checkpoint file(s) in {source_dir}")
    print(f"Target directory: {target_dir}")
    print()

    converted = 0
    for checkpoint_file in checkpoint_files:
        if convert_checkpoint(checkpoint_file, target_dir):
            converted += 1
        print()

    print(f"Converted {converted}/{len(checkpoint_files)} checkpoint(s).")


if __name__ == "__main__":
    main()
