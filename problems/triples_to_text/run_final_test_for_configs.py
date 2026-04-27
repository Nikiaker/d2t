import argparse
import os
import subprocess
import sys
from pathlib import Path


def _relative_depth(root: Path, current: Path) -> int:
    rel = current.relative_to(root)
    if rel == Path("."):
        return 0
    return len(rel.parts)


def find_config_files(root: Path, max_depth: int, filename: str = "config_remote.yaml") -> list[Path]:
    matches: list[Path] = []

    for current in root.rglob(filename):
        if _relative_depth(root, current.parent) <= max_depth:
            matches.append(current)

    return sorted(matches)


def pick_shell_file(folder: Path) -> Path | None:
    shell_files = sorted(folder.glob("*.sh"))
    if not shell_files:
        return None
    return shell_files[0]


def run_final_test_in_folder(folder: Path, final_test_path: Path) -> int:
    shell_file = pick_shell_file(folder)
    if shell_file is None:
        print(f"[SKIP] No .sh file found in: {folder}")
        return 1

    webnlg_domain = shell_file.stem

    env = os.environ.copy()
    env["WEBNLG_DOMAIN"] = webnlg_domain
    env["BEST_PROGRAM_PATH"] = "./openevolve_output/best/best_program.py"

    cmd = [sys.executable, str(final_test_path)]

    print(f"[RUN] Folder: {folder}")
    print(f"      WEBNLG_DOMAIN={webnlg_domain}")
    print("      BEST_PROGRAM_PATH=./openevolve_output/best/best_program.py")

    completed = subprocess.run(cmd, cwd=folder, env=env, check=False)
    return completed.returncode


def has_existing_score_file(folder: Path) -> bool:
    return (folder / "scores.json").exists() or (folder / "scores.json").exists()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Find folders containing config_remote.yaml up to max depth and run final_test.py in each."
        )
    )
    parser.add_argument("folder", help="Root folder to start searching from")
    parser.add_argument(
        "max_depth",
        type=int,
        help="Maximum directory depth to search (0 means only the root folder)",
    )
    parser.add_argument(
        "--config-name",
        default="config_remote.yaml",
        help="Config filename to search for (default: config_remote.yaml)",
    )
    parser.add_argument(
        "--skip-existing-score",
        action="store_true",
        help="Skip folders where score.json or scores.json is already present",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = Path(args.folder).resolve()

    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Invalid folder: {root}")

    if args.max_depth < 0:
        raise SystemExit("max_depth must be >= 0")

    final_test_path = Path(__file__).with_name("final_test.py").resolve()
    if not final_test_path.exists():
        raise SystemExit(f"Could not find final_test.py at: {final_test_path}")

    config_files = find_config_files(root, args.max_depth, filename=args.config_name)
    if not config_files:
        print("No matching config files found.")
        return

    print(f"Found {len(config_files)} config file(s).")

    total = 0
    ok = 0
    failed = 0

    for config_file in config_files:
        total += 1
        folder = config_file.parent

        if args.skip_existing_score and has_existing_score_file(folder):
            failed += 1
            print(f"[SKIP] Existing score file found in: {folder}")
            continue

        code = run_final_test_in_folder(folder, final_test_path)

        if code == 0:
            ok += 1
        else:
            failed += 1
            print(f"[FAIL] Exit code {code} in: {folder}")

    print()
    print(f"Finished. Total: {total}, Succeeded: {ok}, Failed/Skipped: {failed}")


if __name__ == "__main__":
    main()
