# Coding standards

How this project is organised. Godot 4.7.2, GDScript only. Words in **bold** are defined in `CONTEXT.md`.

## Layout

Folders are by feature:

| Folder | What goes there |
|---|---|
| `addons/` | Vendored plugins at pinned versions. Left exactly as vendored. |
| `core/<system>/` | One folder per autoload: `core/events/`, `core/audio/`, `core/scene_flow/`, `core/settings/`, `core/dev_console/`. |
| `ui/` | Main menu, settings panel, pause menu, the shared Theme, shared widgets. |
| `game/` | The **example game scene**, replaced on jam day. |
| `shared/` | Assets used by more than one feature: soft-look environment, toon shader, fonts, `shared/audio/`. |
| `test/` | gdUnit4 tests. |
| `tools/` | `check.py` and its helper scripts. Not exported. |

A file lives in the folder of the only feature that uses it. Move it to `shared/` when a second feature needs it.

## Naming

Follow the [Godot GDScript style guide](https://docs.godotengine.org/en/4.7/tutorials/scripting/gdscript/gdscript_styleguide.html) verbatim:

- snake_case folders and files, PascalCase node names and `class_name`, snake_case functions and variables, CONSTANT_CASE constants, a leading `_` for private members.
- Signals are past tense: `piece_placed`, `level_completed`.
- A scene and its script share a base name and sit side by side: `main_menu.tscn` + `main_menu.gd`.
- Add `class_name` only when another script refers to the type by name: a custom Resource, a component, an `is` check, a typed variable.

`gdlint` enforces most of this. `uv run tools/check.py lint` runs it.

## Static typing

Every declaration is typed: variables, parameters, return types, loop variables. The `untyped_declaration` warning is an **Error** in `project.godot`, so an untyped script fails to load. Inferred types (`:=`) count as typed.

```gdscript
var speed := 4.0
var target: Node3D
func place(at: Vector3) -> void:
for piece: Node3D in pieces:
```

## Autoloads (core systems)

| Autoload | Folder | What it does |
|---|---|---|
| `Events` | `core/events/` | The **signal bus**: every **bus event**, declared in `events.gd`. |
| `Audio` | `core/audio/` | Music crossfade and pooled SFX: `play_music(stream)`, `stop_music()`, `play_sfx(stream)`. |
| `SceneFlow` | `core/scene_flow/` | Moves between top-level scenes with a fade: `await SceneFlow.go_to(path)`. |
| `Settings` | `core/settings/` | The player's **settings**, saved to `user://settings.cfg` on every change. |
| `LimboConsole` | `addons/limbo_console/` | The dev console (plugin). Editor and desktop only; see Dev console. |
| `DevConsole` | `core/dev_console/` | Loads `dev_commands.gd` when `LimboConsole` is running. See Dev console. |

Add an autoload only for a service that must outlive a scene change, or that has exactly one instance game-wide. It lives in `core/<name>/`, works without knowing what the current scene is, and gets a row in this table.

## Scene composition

Call down, signal up.

- A parent calls methods on its children. A child tells its parent things by emitting a local signal.
- A scene reaches its own nodes through unique names: mark the node `unique_name_in_owner` and write `%Button`.
- Dependencies from outside the scene come in through `@export` vars or a setter the parent calls.
- Scenes stay unaware of their surroundings: no `get_parent()`, no `../` paths, no `/root/...` paths.
- Every scene instantiates on its own without errors, so it runs with F6 in the editor, `uv run tools/check.py smoke <scene>`, and a gdUnit4 `scene_runner`.

## Signals: local or bus

Use a local signal by default.

Put a signal on `Events` only for a **bus event**: a broadcast fact that parts of the game which don't know each other react to. Bus events are:

- past tense, with typed parameters,
- documented with a `##` comment,
- declared in `core/events/events.gd`, and added only when something listens.

```gdscript
## A piece was placed on the board at [param position] (world space).
signal piece_placed(position: Vector3)
```

A **command** to a core system is a direct autoload call: `SceneFlow.go_to(...)`, `Audio.play_sfx(...)`. Commands are never bus signals, so a `*_requested` signal is a sign that you need a direct call instead.

Core systems emit on `Events` and declare no public signals of their own. Consumers read a setting from `Settings` when they use it.

## UI

Build UI from Containers (`VBoxContainer`, `MarginContainer`, `CenterContainer`, …) styled by the shared Theme in `ui/`. Containers keep text edits to `.tscn` predictable and scale with the `canvas_items` stretch mode. Set anchors only on the root Control of a scene.

## Editing `.tscn` and `.tres`

Agents may hand-edit any `.tscn` or `.tres` as text, visual properties included. Use the `edit-tscn` skill, which covers `uid://` references and `unique_id`, and run `uv run tools/check.py load` after every edit.

After a visual change, capture the scene (`uv run tools/check.py capture <scene>`) and look at the frame. When the change is about feel (the soft look, lighting, camera, motion), end the handoff with "Needs a visual check: `<scene>`". Tuning by eye in the editor is recommended, never required.

## Tests

- `test/` mirrors the `res://` path of what it tests, and files are named `<name>_test.gd`: `core/audio/audio.gd` → `test/core/audio/audio_test.gd`.
- The Web export drops `test/`.
- The `gdunit-tests` skill has the gdUnit4 patterns.

## Assets

- Commit models as exported `.glb`. Keep `.blend` sources with the modeller, outside the repo: importing `.blend` needs Blender on every machine and in CI.
- No Git LFS. Question or compress any single asset over about 10 MB.
- Commit every `*.uid` and `*.import` file Godot creates next to your files.

## Merges

Godot scenes merge badly, so prevent conflicts:

- Keep scenes small and composed. One person (and their agent) works on a scene at a time; claim it in team chat.
- Pull or rebase with the editor closed, or at least the affected scenes. The editor overwrites pulled changes when it saves its in-memory copy.
- A conflicted `.tscn` or `.tres`: take one side whole (`git checkout --ours <file>` or `--theirs`), redo the other change by hand, then run `uv run tools/check.py load`.
- `project.godot` is INI and can be hand-merged.

## Dev console

`LimboConsole` is left out of the web build, so any script that names it fails to compile there. All console code lives in `core/dev_console/dev_commands.gd`, which is also left out of the web build. The `DevConsole` autoload loads it only when `get_tree().root.get_node_or_null(^"LimboConsole")` exists. Add new console commands there; open the console with F1 in an editor run. F1 is the same key on every keyboard layout; a backtick toggle can't be typed on Nordic layouts.

The web build logs one `Failed to instantiate an autoload` error at startup, for the missing `LimboConsole`. That line is expected.
