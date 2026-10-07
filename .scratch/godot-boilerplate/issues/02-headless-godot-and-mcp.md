# What can agents do with headless Godot alone, and which Godot MCP server (if any) fills the gaps?

Type: research
Status: resolved
Blocked by:

## Question

Agents should prefer headless Godot (4.7.2 CLI) and fall back to MCP only when needed. Find out:

- What the Godot 4.7 CLI can do headlessly: `--headless`, `--check-only` / script parse checking, `--import` / reimport, running a scene or script (`-s`), running gdUnit4 tests headless, `--export-release` for web, `--quit-after`, capturing errors/output, screenshot capture options.
- Gaps an agent hits without the editor running (e.g. inspecting the live scene tree, visual verification, editing .tscn safely).
- The landscape of Godot MCP servers usable from Claude Code: maintained ones, what tools they expose, Godot 4.7 compatibility, install effort, and whether they need the editor open.

## Answer

- **Headless Godot covers what agents need day to day.** That means `--import`, script compile checks, gdUnit4 tests (`runtest.sh --headless --ignoreHeadlessMode`; exit 100 on failures), smoke runs (`--quit-after N --log-file`), and web export (`--export-release`, which needs the exact 4.7.2 templates). Every command was run on the 4.7.2 binary. The export test used 4.7.1 web templates.
- **Don't use bare `--check-only` as the gate.**
  - Its exit code is always 0 on macOS; Linux correctly returns 1.
  - It flags every reference to an autoload as an error, even after `--import` (upstream #78587).
  - Instead, gate on a small `SceneTree` script that `load()`s every `.gd` and calls `quit(1)` on failure. It's verified on macOS with 4.7.2, has autoloads available, and returns the right exit code.
- **Runtime errors and `push_error` exit 0.** Smoke runs have to grep stderr or the log for `ERROR`. Never pass `-d` without `--remote-debug tcp://127.0.0.1:0`, or a script error hangs the run.
- **Visual checks need a window.** `--write-movie` crashes headless but works windowed on a Mac, so an agent can capture PNG frames and look at them. Programmatic `.tscn` edits through `PackedScene.pack()` + `ResourceSaver.save()` work headless.
- **MCP: none required.** The most-starred server (Coding-Solo) only wraps the same CLI commands. If an optional server gets documented for live-game screenshots, input and the scene tree with the editor open, **hi-godot/godot-ai** is the candidate: MIT, active, targets 4.7+, telemetry on by default. Spike it before recommending it, since nothing in the MCP survey was installed or run.
- **These stay human editor tasks:** judging the look and feel, UI layout, import tuning, playtesting, and breakpoint debugging.

[findings](../research/02-headless-godot-and-mcp.md)
