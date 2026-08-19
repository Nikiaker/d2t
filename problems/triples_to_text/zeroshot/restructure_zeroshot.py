import argparse
import shutil
import sys
from pathlib import Path


def restructure_domain_folder(domain_dir: Path, dry_run: bool = False) -> bool:
    if not domain_dir.is_dir() or not domain_dir.name.endswith("_output"):
        return False

    best_program = domain_dir / "best_program.py"
    generated_texts = domain_dir / "generated_texts.json"
    config_remote = domain_dir / "config_remote.yaml"
    
    domain_name = domain_dir.name.removesuffix("_output")
    sh_file = domain_dir / f"{domain_name}.sh"

    if not best_program.exists() and not generated_texts.exists():
        return False

    target_dir = domain_dir / "openevolve_output" / "best"

    if dry_run:
        print(f"[DRY-RUN] Would restructure: {domain_dir.name}")
        if best_program.exists():
            print(f"  Move: {best_program.name} -> {target_dir.relative_to(domain_dir) / best_program.name}")
        if generated_texts.exists():
            print(f"  Move: {generated_texts.name} -> {target_dir.relative_to(domain_dir) / generated_texts.name}")
        if not config_remote.exists():
            print(f"  Create: config_remote.yaml")
        if not sh_file.exists():
            print(f"  Create: {sh_file.name}")
        return True

    target_dir.mkdir(parents=True, exist_ok=True)

    moved_any = False
    for src_file in [best_program, generated_texts]:
        if not src_file.exists():
            continue

        dst_file = target_dir / src_file.name
        if dst_file.exists():
            print(f"[SKIP] Already exists: {dst_file.relative_to(domain_dir)}")
            continue

        shutil.move(str(src_file), str(dst_file))
        print(f"[MOVE] {src_file.name} -> {dst_file.relative_to(domain_dir)}")
        moved_any = True

    if not config_remote.exists():
        config_remote.touch()
        print(f"[CREATE] config_remote.yaml")
        moved_any = True

    if not sh_file.exists():
        sh_file.write_text("#!/bin/bash\n")
        print(f"[CREATE] {sh_file.name}")
        moved_any = True

    return moved_any


def main():
    parser = argparse.ArgumentParser(
        description="Restructure existing zeroshot output folders to match the new openevolve_output/best/ layout."
    )
    parser.add_argument(
        "root",
        help="Root folder containing <Domain>_output subdirectories (e.g., outputs/zeroshot/)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists() or not root.is_dir():
        print(f"Error: Invalid root folder: {root}", file=sys.stderr)
        sys.exit(1)

    domain_dirs = sorted([d for d in root.iterdir() if d.is_dir() and d.name.endswith("_output")])

    if not domain_dirs:
        print(f"No <Domain>_output directories found in {root}")
        sys.exit(0)

    print(f"Found {len(domain_dirs)} domain output folder(s) in {root}")
    print()

    restructured = 0
    for domain_dir in domain_dirs:
        if restructure_domain_folder(domain_dir, dry_run=args.dry_run):
            restructured += 1

    print()
    action = "Would restructure" if args.dry_run else "Restructured"
    print(f"{action} {restructured} folder(s).")


if __name__ == "__main__":
    main()
