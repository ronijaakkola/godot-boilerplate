# /// script
# requires-python = ">=3.10"
# dependencies = ["gdtoolkit==4.5.0"]
# ///
"""Project checks. Run from anywhere: `uv run tools/check.py <command>`.

  lint [files]     gdlint the given .gd files, or the whole project (no Godot needed)
  lint --hook      Claude Code PostToolUse hook: lint the edited file, exit 2 on problems
  load             compile every script outside addons/ (the load check)
  test             run the gdUnit4 tests in test/
  smoke [scene]    run the main scene (or the given one) headless, fail on any logged error
  capture <scene>  render ~1 s of a scene in a window, save the frames to build/capture/
  all              lint, load, test, smoke
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from importlib.metadata import version as pkg_version
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GODOT_VERSION = "4.7.2"
TIMEOUT = 300
SMOKE_FRAMES = "300"
CAPTURE_FRAMES = "60"
ERROR_LINE = re.compile(r"^(SCRIPT )?ERROR", re.MULTILINE)
ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
# Godot 4.7.2 leaks an Ogg stream that is still playing when it quits, so any scene
# with music logs this at the end of a smoke run. It happens only at exit.
EXIT_LEAK = re.compile(r"^ERROR: \d+ resources still in use at exit.*$", re.MULTILINE)


class CheckFailed(Exception):
    pass


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    commands = parser.add_subparsers(dest="command", required=True)
    lint = commands.add_parser("lint")
    lint.add_argument("files", nargs="*")
    lint.add_argument("--hook", action="store_true")
    commands.add_parser("load")
    commands.add_parser("test")
    commands.add_parser("smoke").add_argument("scene", nargs="?")
    commands.add_parser("capture").add_argument("scene")
    commands.add_parser("all")
    args = parser.parse_args()
    os.chdir(ROOT)

    if args.command == "lint" and args.hook:
        return lint_hook()
    steps = {
        "lint": lambda: run_lint(getattr(args, "files", [])),
        "load": run_load,
        "test": run_test,
        "smoke": lambda: run_smoke(getattr(args, "scene", None)),
        "capture": lambda: run_capture(args.scene),
    }
    names = ["lint", "load", "test", "smoke"] if args.command == "all" else [args.command]
    failed = [name for name in names if not run_step(name, steps[name])]
    if args.command == "all":
        print("FAIL all: " + ", ".join(failed) if failed else "PASS all")
    return 1 if failed else 0


def run_step(name, step) -> bool:
    try:
        note = step()
    except CheckFailed as failure:
        print(f"FAIL {name}: {failure}")
        return False
    print(f"PASS {name}" + (f": {note}" if note else ""))
    return True


# --- lint -------------------------------------------------------------------


def lintable(path: str) -> bool:
    """A .gd file outside addons/. gdlint ignores its excluded_directories for
    explicit file paths (gdtoolkit#395), so explicit paths are filtered here."""
    relative = Path(os.path.relpath(Path(path).resolve(), ROOT))
    return relative.suffix == ".gd" and relative.parts[0] not in ("addons", "..")


def gdlint(paths: list[str]) -> subprocess.CompletedProcess:
    # gdtoolkit creates its grammar cache folder racily (gdtoolkit#428): parallel
    # hook runs on a cold cache crash. Creating it first avoids that.
    from gdtoolkit.parser.parser import get_cache_directory

    cache = Path(get_cache_directory(), "gdtoolkit", pkg_version("gdtoolkit"))
    cache.mkdir(parents=True, exist_ok=True)
    return subprocess.run(
        [sys.executable, "-m", "gdtoolkit.linter", *paths],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def run_lint(files: list[str]):
    paths = [f for f in files if lintable(f)] if files else ["."]
    if not paths:
        return "no .gd files outside addons/"
    result = gdlint(paths)
    if result.returncode != 0:
        print(result.stderr, end="")
        raise CheckFailed("gdlint found problems")
    return None


def lint_hook() -> int:
    file_path = json.load(sys.stdin).get("tool_input", {}).get("file_path", "")
    if not file_path or not lintable(file_path):
        return 0
    result = gdlint([file_path])
    if result.returncode != 0:
        print(result.stderr, end="", file=sys.stderr)
        return 2
    return 0


# --- Godot ------------------------------------------------------------------

_godot: str | None = None


def godot() -> str:
    """Finds Godot 4.7.2 and imports the project once per run. Importing every
    time keeps the global class cache current, so a new class_name resolves."""
    global _godot
    if _godot:
        return _godot
    binary = os.environ.get("GODOT") or shutil.which("godot")
    found = ""
    if binary:
        try:
            found = subprocess.run(
                [binary, "--version"], capture_output=True, text=True, timeout=30
            ).stdout.strip()
        except OSError:
            found = ""
    if not found.startswith(GODOT_VERSION + "."):
        raise CheckFailed(
            f"Godot {GODOT_VERSION} not found (got {found or binary or 'nothing'}). "
            "Set GODOT to its path, e.g. Windows: "
            'setx GODOT "C:\\Godot\\Godot_v4.7.2-stable_win64_console.exe", '
            "Mac: export GODOT=/Applications/Godot.app/Contents/MacOS/Godot"
        )
    # build/ holds exports, reports and captures. A .gdignore keeps Godot from importing it.
    Path("build").mkdir(exist_ok=True)
    Path("build/.gdignore").touch()
    # The import's exit code can't be trusted (it sometimes crashes on exit
    # after finishing), so check for its output instead.
    run([binary, "--headless", "--path", ".", "--import"])
    if not Path(".godot/global_script_class_cache.cfg").exists():
        raise CheckFailed("godot --import did not write .godot/global_script_class_cache.cfg")
    _godot = binary
    return binary


def run_godot(args: list[str]) -> subprocess.CompletedProcess:
    """Never pass -d without --remote-debug: a script error would wait for
    debugger input forever."""
    return run([godot(), *args])


def run(command: list[str]) -> subprocess.CompletedProcess:
    """Runs a command with stdout and stderr merged and colour codes stripped."""
    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=TIMEOUT,
        )
    except subprocess.TimeoutExpired as timeout:
        raise CheckFailed(f"Godot timed out after {TIMEOUT} s: {' '.join(command)}") from timeout
    result.stdout = ANSI.sub("", result.stdout)
    return result


def ensure_build_dir(path: str) -> Path:
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def run_load():
    result = run_godot(["--headless", "--path", ".", "-s", "res://tools/load_check.gd"])
    summary = re.search(r"^checked (\d+), failures: (\d+)$", result.stdout, re.MULTILINE)
    # A parse error in load_check.gd itself makes Godot exit 0 with no summary.
    if not summary:
        print(result.stdout, end="")
        raise CheckFailed("the load check script did not run")
    if result.returncode != 0 or summary.group(2) != "0":
        print(result.stdout, end="")
        raise CheckFailed(f"{summary.group(2)} of {summary.group(1)} files failed to load")
    # A scene with a missing dependency still loads, but logs an error.
    if ERROR_LINE.search(result.stdout):
        print(result.stdout, end="")
        raise CheckFailed("errors logged while loading")
    return f"{summary.group(1)} files"


def run_test():
    ensure_build_dir("build/reports")
    result = run_godot(
        [
            "--headless", "--path", ".",
            "-s", "-d", "--remote-debug", "tcp://127.0.0.1:0",
            "res://addons/gdUnit4/bin/GdUnitCmdTool.gd",
            "-a", "res://test", "-c", "-rd", "res://build/reports", "--ignoreHeadlessMode",
        ]
    )  # fmt: skip
    if "No test cases found" in result.stdout:
        return "no tests in test/"
    if result.returncode not in (0, 101):
        print(result.stdout, end="")
        raise CheckFailed(f"gdUnit4 exit code {result.returncode} (report in build/reports/)")
    summary = re.search(r"^Overall Summary: (\d+) test cases", result.stdout, re.MULTILINE)
    return f"{summary.group(1)} tests" if summary else None


def main_scene() -> str | None:
    match = re.search(
        r'^run/main_scene="([^"]+)"', Path("project.godot").read_text(), re.MULTILINE
    )
    return match.group(1) if match else None


def logged_error(output: str) -> bool:
    return bool(ERROR_LINE.search(EXIT_LEAK.sub("", output)))


def run_smoke(scene: str | None):
    scene = scene or main_scene()
    if not scene:
        return "SKIPPED, no main scene set in project.godot"
    result = run_godot(
        ["--headless", "--path", ".", "--scene", scene, "--quit-after", SMOKE_FRAMES]
    )
    if logged_error(result.stdout):
        print(result.stdout, end="")
        raise CheckFailed(f"errors logged while running {scene}")
    return scene


def run_capture(scene: str):
    """Windowed only: --write-movie crashes under --headless."""
    directory = ensure_build_dir("build/capture")
    for old in directory.iterdir():
        old.unlink()
    result = run_godot(
        [
            "--path", ".", "--scene", scene,
            "--write-movie", str((directory / "frame.png").resolve()),
            "--quit-after", CAPTURE_FRAMES,
        ]
    )  # fmt: skip
    (directory / "frame.wav").unlink(missing_ok=True)
    frames = sorted(directory.glob("frame*.png"))
    if not frames:
        print(result.stdout, end="")
        raise CheckFailed(f"no frames written for {scene}")
    errors = " (errors logged, see above)" if logged_error(result.stdout) else ""
    if errors:
        print(result.stdout, end="")
    return f"{len(frames)} frames, look at {frames[-1].as_posix()}{errors}"


if __name__ == "__main__":
    sys.exit(main())
