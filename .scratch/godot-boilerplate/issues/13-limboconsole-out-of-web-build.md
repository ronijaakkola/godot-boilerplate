# Keep LimboConsole out of the web build and add dev commands

Type: task
Status: resolved
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

## Answer

Built in `feat(dev-console): keep LimboConsole out of the web build and add goto` (4083ebd). `check.py all` passes: 20 tests, smoke on the main menu. The deploy run on `main` succeeded.

- **Exclusion:** the Web `exclude_filter` adds `addons/limbo_console/*, addons/limbo_console.cfg, core/dev_console/dev_commands.gd`. LimboConsole's own export plugin still `add_file`s `limbo_console.cfg` into the pack, so it ships anyway. It's a few hundred bytes and harmless.
- **Size:** the local export's `index.pck` is 1.27 MB, down from 8.9 MB. The menu music is 1.2 MB of that, so our code and scenes are about 70 KB.
- **Boot:** the pack runs headless (`--main-pack`, 300 frames, exit 0) with one autoload failure. That one failure logs three `ERROR` lines: the script open, the resource load and "Failed to instantiate an autoload". The only other lines are the at-exit Ogg leak (an ObjectDB warning and "resources still in use"), which a normal project run logs too.
- **Loader (not in the design, decided here):** `dev_commands.gd` can't be an autoload itself. Excluded, it adds a second autoload failure. Shipped, it fails to compile without `LimboConsole`. So a new `DevConsole` autoload (`core/dev_console/dev_console.gd`, after `LimboConsole` in the list) checks `get_node_or_null(^"LimboConsole")` and `load()`s the commands as its child at runtime. It names neither at compile time, so it ships to the web and does nothing there. It has a row in the `CODING_STANDARDS.md` autoload table.
- **Command:** `goto <scene path>` checks `ResourceLoader.exists` (it prints a console error if not) and calls `SceneFlow.go_to(path)` without awaiting. `test/core/dev_console/dev_commands_test.gd` runs `goto res://game/game.tscn` through the live console's `execute_command` and checks the scene changed, then waits out the fade-in so the next suite starts with input on. It reaches the console by node path, so `dev_commands.gd` stays the only script that names it.
- **Docs:** `CODING_STANDARDS.md` Dev console section now names `DevConsole`, says `dev_commands.gd` is excluded too, and calls the startup autoload error expected.
- **Not checked by hand:** opening the console with F1 in an editor run (Cmd+B on a Mac) and typing `goto res://game/game.tscn`. The test covers the same command path headlessly. A real browser run of the console-free build will come from the next itch deploy.
- **Toggle key:** rebound from `` ` `` to F1 after the user asked how to open the console on a Mac. On Finnish/Swedish layouts the key left of 1 is `§`, and backtick is a dead key, so the `` ` `` toggle couldn't be pressed.
