# Agent guidance

Type: grilling
Status: open
Blocked by: 02, 04

## Question

What do agents get: contents of `CLAUDE.md` (conventions, do/don't list, verification loop), which project skills to write under `.claude/skills/` (e.g. running headless Godot, writing gdUnit4 tests, adding a scene/system, editing .tscn safely), the Claude Code PostToolUse hook that runs gdformat/gdlint on edited `.gd` files, and the rule for headless CLI vs MCP.

Note (from ticket 02): decide whether to document hi-godot/godot-ai as an optional MCP (editor-open screenshots/input/live tree) — it needs ~1h trial on 4.7.2 first, and telemetry is on by default (`GODOT_AI_DISABLE_TELEMETRY=true`). Headless `.tscn` edits via `PackedScene.pack()` rewrite ids and add `unique_id=` on save — relevant to the .tscn editing rule.

Note (from ticket 03): hooks must run `gdlint` + `gdformat --check` only, never auto-format (gdformat can produce code Godot rejects, gdtoolkit#424, and duplicates comments); exclude `addons/` explicitly (#395); never run two instances concurrently (#428).

Note (from ticket 04): `CLAUDE.md` must carry the conventions from ticket 04: layout and placement rule, naming and `class_name` policy, autoload rule, composition rules, bus rule, `.tscn` hand-edit safety rules, Containers + Theme for UI, merge policy (pull with the editor closed). Agents self-check visual changes with windowed `--write-movie` frame capture and flag feel-changes as "needs a visual check". Decide whether the godot-ai MCP replaces or adds to frame capture.

Note (from ticket 05): the whole-project load-check script from ticket 02 §1.1 isn't in the repo yet, and the layout has no `tools/` folder. Decide where it lives. `gdlintrc` already excludes `addons/` and `.godot/` for directory runs. The ticket-02 note "macOS `--check-only` exits 0" still holds: `README.md` currently only lists import, lint and export.
