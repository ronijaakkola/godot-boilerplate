# Build the agent guidance

Type: task
Status: open
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
