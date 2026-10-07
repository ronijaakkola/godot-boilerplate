# Agent guidance

Type: grilling
Status: resolved
Blocked by: 02, 04

## Question

What do agents get: contents of `CLAUDE.md` (conventions, do/don't list, verification loop), which project skills to write under `.claude/skills/` (e.g. running headless Godot, writing gdUnit4 tests, adding a scene/system, editing .tscn safely), the Claude Code PostToolUse hook that runs gdformat/gdlint on edited `.gd` files, and the rule for headless CLI vs MCP.

Note (from ticket 02): decide whether to document hi-godot/godot-ai as an optional MCP (editor-open screenshots/input/live tree) — it needs ~1h trial on 4.7.2 first, and telemetry is on by default (`GODOT_AI_DISABLE_TELEMETRY=true`). Headless `.tscn` edits via `PackedScene.pack()` rewrite ids and add `unique_id=` on save — relevant to the .tscn editing rule.

Note (from ticket 03): hooks must run `gdlint` + `gdformat --check` only, never auto-format (gdformat can produce code Godot rejects, gdtoolkit#424, and duplicates comments); exclude `addons/` explicitly (#395); never run two instances concurrently (#428).

Note (from ticket 04): `CLAUDE.md` must carry the conventions from ticket 04: layout and placement rule, naming and `class_name` policy, autoload rule, composition rules, bus rule, `.tscn` hand-edit safety rules, Containers + Theme for UI, merge policy (pull with the editor closed). Agents self-check visual changes with windowed `--write-movie` frame capture and flag feel-changes as "needs a visual check". Decide whether the godot-ai MCP replaces or adds to frame capture.

Note (from ticket 05): the whole-project load-check script from ticket 02 §1.1 isn't in the repo yet, and the layout has no `tools/` folder. Decide where it lives. `gdlintrc` already excludes `addons/` and `.godot/` for directory runs. The ticket-02 note "macOS `--check-only` exits 0" still holds: `README.md` currently only lists import, lint and export.

## Answer

- **The wrapper `tools/check.py` owns every Godot flag.** It runs with `uv run` on Windows and Mac; the team is mixed, so bash would leave out PowerShell users. Its header pins gdtoolkit 4.5.0 (PEP 723 inline deps).
  - **Subcommands:** `lint [files]`, `load`, `test`, `smoke`, `capture <scene>`, and `all` (lint + load + test + smoke). Each prints PASS or FAIL and returns a correct exit code on both OSes. It runs `--import` first if `.godot/` is missing.
  - **Finding Godot:** the `GODOT` env var, else `godot` on the PATH, and the version must be `4.7.2`. Otherwise it stops with one line telling the user to set `GODOT` (with a `setx` example). `lint` never needs Godot.
  - **Facts the build has to respect:**
    - The load check is a fully typed SceneTree script that runs `load()` on every `.gd` outside `addons/` and calls `quit(1)` if any `(s as GDScript).can_instantiate()` is false. `load()` returns a non-null script even when it has parse errors, and if the check script itself fails to parse, Godot exits 0.
    - A smoke run must grep the log for `^(SCRIPT )?ERROR`.
    - `capture` runs windowed with `--write-movie`, never headless.
    - Tests call gdUnit4's CLI tool through Godot, not `runtest.sh`/`.cmd`.
    - Never `-d` without `--remote-debug`.
    - `godot --headless --quit` hangs on this project (no main scene), so every run gets `-s` or `--scene` plus `--quit-after`.
  - `tools/` joins the Web preset's `exclude_filter`. CI reuses the same subcommands.
- **No gdformat anywhere, lint only.** This reverses part of the plugins/CI research. gdformat 4.5.0 has no off comment (upstream #52 is open), it can produce code Godot rejects (#424), and code written in the editor would always fail `--check`. The style rules that matter are already gdlint rules.
- **Hooks:**
  - The committed `.claude/settings.json` has a PostToolUse hook with matcher `Edit|Write` that runs `check lint <file>` for `.gd` files outside `addons/`. It reads `tool_input.file_path` from stdin, filters `addons/` itself because gdlint's `excluded_directories` ignores explicit file paths (#395), and runs from the repo root so `gdlintrc` is found. Problems go to stderr with exit 2, which feeds them back to the agent.
  - Lint only in this hook: a load check would fire on half-finished edits that span several files.
  - PostToolUse runs concurrently for parallel edits, so `check.py` creates gdtoolkit's cache folder before parsing, which avoids the cold-cache race (#428).
  - The same file allowlists `uv run tools/check.py` and `uvx --from gdtoolkit==4.5.0`. Rules match the literal command text, so docs always write exactly `uv run tools/check.py …`. Personal overrides go in `settings.local.json`.
  - `.githooks/pre-commit` also runs `check lint` on staged `.gd` files outside `addons/`. It needs uv, not Godot.
- **One job per doc:**
  - **`CLAUDE.md`**, about 40 lines, Godot project only:
    - Pointers to the other docs.
    - The `check` subcommands and when to run each: the hook lints, `check all` before handoff, `check capture <scene>` after any visual change and the agent looks at the frame.
    - "Needs a visual check: <scene>" for feel changes.
    - **Honest handoffs:** if a check couldn't run (for example, Godot not found), say so and name the editor equivalent: F5, the gdUnit panel.
    - The trigger line: before touching shaders, environment, lighting, loading or audio, read `docs/web-constraints.md`.
    - Read `DESIGN.md` before gameplay work and update it when the design changes.
  - **`CODING_STANDARDS.md`:** the conventions from the folder-layout ticket, plus the console rule (LimboConsole only in `dev_commands.gd`).
  - **`DESIGN.md`:** what the game is. Pitch, core loop, controls, scenes and flow, scope. It ships now describing the example game scene, and on jam day the content is replaced and the headings stay.
  - **`CONTEXT.md`:** the glossary only.
  - **`docs/web-constraints.md`:** the web limits from the renderer research (Compatibility/WebGL2, the effects that work, no threads, audio unlock, save on every change). It's in `docs/` rather than a skill so that humans tuning the look find it too.
- **Two project skills in `.claude/skills/`:**
  - `gdunit-tests`: gdUnit4 v6 tests in this repo. Placement, scene runner, simulated mouse input, awaiting signals, reading failures.
  - `edit-tscn`: hand-editing `.tscn`/`.tres`. `uid://` refs, never write `unique_id`, resource ids, Containers + Theme, then `check load`.
  - Adding a scene or a core system is covered by `CODING_STANDARDS.md`, so neither gets a skill. Third-party packs (e.g. GodotPrompter, 56 skills) are left out because they'd compete with our conventions. Anyone may install them personally.
- **The repo carries only the project's own guidance.** Personal setups (user-level `CLAUDE.md`, Pocock skills) are not packaged. The map and issue-tracker sections leave `CLAUDE.md` at jam-day handoff (see the map's fog).
- **Editor-only humans:** every `check` subcommand has an editor equivalent, listed in the README: the error list or F5, the gdUnit panel, F5/F6 with Output, looking at the game, and pre-commit lint. With a broken PATH, agents still edit and lint normally. They only lose `load`/`test`/`smoke`/`capture`, and they report that at handoff.
- **MCP:** none, and no godot-ai trial in this effort (out of scope).
- **Windows** is unverified until the build ticket's HITL checklist runs on a Windows machine.

