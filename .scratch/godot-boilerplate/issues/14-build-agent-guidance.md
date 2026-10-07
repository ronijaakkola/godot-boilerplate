# Build the agent guidance

Type: task
Status: claimed
Blocked by: 07

## Question

AFK build per the [agent guidance decision](07-agent-guidance.md), then one HITL step on Windows. Use `/writing-for-agents` for `CLAUDE.md`, the skills and the docs.

- **`tools/check.py`**, run with `uv run` and gdtoolkit 4.5.0 pinned inline. Subcommands `lint [files]`, `load`, `test`, `smoke`, `capture <scene>`, `all`. Godot comes from `GODOT` or the PATH, and must be 4.7.2. The load check is a typed SceneTree script under `tools/`. Add `tools/*` to the Web `exclude_filter`.
- **Hooks:**
  - `.claude/settings.json` with the PostToolUse `Edit|Write` lint hook (`.gd` only, `addons/` filtered, exit 2 on problems) and the permission allowlist.
  - Lint of staged `.gd` files in `.githooks/pre-commit`, keeping the merge-commit block.
- **Docs:**
  - `CLAUDE.md`: Godot guidance added above the existing sections. The map and issue-tracker sections stay until jam-day handoff.
  - `CODING_STANDARDS.md`: the folder-layout ticket's conventions.
  - `DESIGN.md`: the example game scene, under the fixed headings.
  - `docs/web-constraints.md`: from the renderer research.
  - Skills `.claude/skills/gdunit-tests/` and `.claude/skills/edit-tscn/`.
  - README: `check` commands in place of the raw Godot commands, editor equivalents, and the Windows `GODOT` setup step.
- **Tests:** `test/` is empty until the audio and settings build. Write one trivial test so `check test` and `check all` can be shown passing, or make an empty suite a pass, whichever gdUnit4 allows.

Done when:
- On the Mac, `uv run tools/check.py all` passes. A deliberately broken script fails `load`, a `push_error` fails `smoke`, and `capture` writes a PNG of a scene.
- An agent edit that breaks a lint rule gets the problem fed back by the hook.
- A commit with a lint error is blocked.
- **HITL on Windows:** clone, set `GODOT`, run `check all`, make one lint-failing edit through Claude Code and one commit. Record the results here, or "Windows untested" if nobody is available before November.

## Comments

- From the CI pipeline ticket: the Web `exclude_filter` is `addons/gdUnit4/*, test/*, build/*`. It does **not** include `tools/*` yet, despite an earlier note saying it did, so add it when creating `tools/`. Once `check.py` exists, add a CI job (or a step in `pr-tests.yml`) that runs `uv run tools/check.py lint load smoke` on Linux. It needs `astral-sh/setup-uv` and `GODOT` pointing at a 4.7.2 binary; gdUnit4-action installs Godot at `/home/runner/godot-linux/godot`, or use `setup-godot`.
- Progress (2026-10-07), [PR #2](https://github.com/ronijaakkola/godot-boilerplate/pull/2):
  - **Built and verified on the Mac:** `tools/check.py` + `tools/load_check.gd`, staged-file lint in `pre-commit`, the CI `checks` job, every doc and both skills, `tools/*` in the Web `exclude_filter`. `check all` passes. A broken script fails `load`, a `push_error` fails `smoke`, `capture` writes 60 PNGs, and a lint error blocks a commit. The hook mode passes when PostToolUse JSON is piped into it, including six parallel runs on a cold gdtoolkit cache. CI `checks` and `test` are green on the PR.
  - **Open:** `.claude/settings.json` (hook + allowlist). The auto-mode classifier refused to let the agent write it, so the user creates it, and then the hook gets tested end-to-end with a real agent edit. The Windows HITL run is also still open.
  - **Deviations from the Agent guidance decision, found while building:**
    - `check.py` runs `--import` (about 1.5 s) before every Godot step, not only when `.godot/` is missing. Without it, a newly added `class_name` fails `load` until the next import.
    - `load` also loads every `.tscn`/`.tres` and fails on any logged `ERROR` line. A scene with a missing `ext_resource` still loads, but logs an error.
    - `test` passes `-c` (no fail-fast), so every failure in a suite shows. An empty `test/` exits 0 natively, so no placeholder test ships. A test file that fails to parse aborts the run with exit code 105.
    - `smoke` reports SKIPPED while `project.godot` has no main scene. Once SceneFlow and the main menu are built, it runs the menu.
    - The hook command is `uv run "$CLAUDE_PROJECT_DIR/tools/check.py" lint --hook`, which reads the PostToolUse JSON from stdin.
    - The autoload table lives in `CODING_STANDARDS.md`, which `CLAUDE.md` points to, rather than in `CLAUDE.md`.
    - `pre-commit` lints the working-tree version of the staged files, not the staged content.
    - `check.py` writes `build/.gdignore`, so Godot stops importing the PNGs in `build/web/`.
  - **For later tickets:** `await_signal` misses a signal emitted during the call itself; use `monitor_signals` + `assert_signal().is_emitted` (in the `gdunit-tests` skill). Headless scene-runner mouse clicks on Controls and key presses work. 3D physics picking is still untested. `docs/web-constraints.md` links into `.scratch/…/research/`, so that link depends on what jam-day cleanup does with `.scratch/`.
  - **Hook verified end-to-end (2026-10-07):** the user created `.claude/settings.json` (commit `build(claude): add lint hook and check.py allowlist`). An agent `Write` of a `.gd` with a bad function name got the gdlint problem back as a blocking PostToolUse error, without a restart. Both project skills show up in the agent's skill list.
