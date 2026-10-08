# Keep LimboConsole out of the web build and add dev commands

Type: task
Status: open
Blocked by: 11

## Question

AFK build, per the [core-systems design](06-core-systems-design.md).

- **Exclusion:** add `addons/limbo_console/*, addons/limbo_console.cfg` to the Web preset's `exclude_filter`. The one "Failed to instantiate an autoload" boot line is accepted.
- **Dev commands:** add `core/dev_console/dev_commands.gd`, the only script that may name `LimboConsole`. Load it only when `get_tree().root.get_node_or_null(^"LimboConsole")` exists, and exclude it from the Web preset.
- **Command:** register `goto <scene path>`, which calls `SceneFlow.go_to`.
- **Docs:** document the rule (console code only in `dev_commands.gd`) where the agent guidance ticket will pick it up.

Done when a local web export's `.pck` is under 1 MB plus our own assets, the exported pack boots (headless `--main-pack`) with only that one error line, and `goto` works in the editor run.

## Comments

- From the agent guidance ticket: the guidance gets built before this ticket, so add the console rule (LimboConsole only in `core/dev_console/dev_commands.gd`) to `CODING_STANDARDS.md` yourself. Done also requires `uv run tools/check.py all` to pass.
- From the SceneFlow and main menu ticket: `goto` calls `SceneFlow.go_to(path)` without awaiting it. A local Web export with the menu music is 8.9 MB of `.pck`; the music alone is 1.2 MB. `check.py smoke` and `capture` now ignore Godot's at-exit "resources still in use" line, which a playing Ogg causes, so don't count that line against the one accepted autoload error.
