# Godot Jam Boilerplate

Godot 4.7.2 GDScript project, web (itch.io) first, Compatibility renderer.

## Setup

1. Install **Godot 4.7.2** exactly. The whole team and CI are pinned to it.
2. Install the **4.7.2 Web export templates**. In the editor: **Editor → Manage Export Templates…**, download only the Web templates. Templates from another version (even 4.7.1) fail with "No export template found".
3. Install [uv](https://docs.astral.sh/uv/). `tools/check.py` runs through it and fetches its own Python packages.
4. Point the checks at Godot. They use the `GODOT` environment variable, or `godot` on the PATH.
   - **Windows:** `setx GODOT "C:\path\to\Godot_v4.7.2-stable_win64_console.exe"`, then open a new terminal and start Claude Code from that one, since terminals that were already open don't see the variable. Use the `_console` executable; the other one prints nothing. Clone to a short path (under about 120 characters). gdUnit4's files and Godot's `.godot/` cache are deeply nested, and git stops at Windows' 260-character limit unless `git config --global core.longpaths true` is set.
   - **Mac:** `export GODOT=/Applications/Godot.app/Contents/MacOS/Godot` in your shell profile, or `brew install godot` if it installs 4.7.2.
5. Enable the git hooks once per clone: `git config core.hooksPath .githooks`.
6. Run `uv run tools/check.py all`. It imports the project and should end with `PASS all`.

## Layout

| Folder | What goes there |
|---|---|
| `addons/` | Vendored plugins at pinned versions. Never hand-edited. |
| `core/<system>/` | One folder per autoload. |
| `ui/` | Main menu, settings screen, Theme, shared widgets. |
| `game/` | The example game scene, replaced on jam day. |
| `shared/` | Assets used by more than one feature. |
| `test/` | gdUnit4 tests, mirroring the `res://` path of what they test. |
| `tools/` | `check.py` and its helper scripts. Not exported. |

## Pinned versions

| Tool | Version |
|---|---|
| Godot | 4.7.2 |
| gdUnit4 | 6.2.1 (`addons/gdUnit4/`) |
| LimboConsole | 0.8.0 (`addons/limbo_console/`) |
| gdtoolkit | 4.5.0 (pinned in `tools/check.py`) |

## Checks

Every check is a `tools/check.py` subcommand, and works the same on Windows, Mac and Linux. Each one prints `PASS` or `FAIL` and exits non-zero on failure. Agents run them; humans working in the editor have an equivalent for each.

| Command | What it does | In the editor |
|---|---|---|
| `uv run tools/check.py lint [files]` | `gdlint` on the given files or the whole project, skipping `addons/`. Runs on every commit and after every Claude Code edit. No Godot needed. | The pre-commit hook does it for you |
| `uv run tools/check.py load` | Loads every script, scene and resource. Fails on parse and type errors and missing dependencies. | Errors in the Output panel, or F5 |
| `uv run tools/check.py test` | Runs the gdUnit4 tests in `test/`. Reports go to `build/reports/`. | The gdUnit panel's run button |
| `uv run tools/check.py smoke [scene]` | Runs the main scene (or the given one) headless for 300 frames and fails if any error is logged. | F5 or F6, then the Output panel |
| `uv run tools/check.py capture <scene>` | Renders a second of the scene in a window and saves the frames to `build/capture/`. | Run the scene and look |
| `uv run tools/check.py all` | `lint`, `load`, `test` and `smoke`. | All of the above |

Web export, for a local test of the itch build:

```sh
mkdir -p build/web && godot --headless --path . --export-release "Web" build/web/index.html
```

Pull requests run two CI checks: `gdUnit4 tests` and `Lint, load check, smoke run`. Both must pass to merge into `main`. Every push to `main` deploys the web build to itch.io.
