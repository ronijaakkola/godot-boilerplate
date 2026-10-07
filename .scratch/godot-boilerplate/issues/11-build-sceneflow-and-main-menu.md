# Build SceneFlow and the main menu

Type: task
Status: open
Blocked by: 10

## Question

AFK build, per the [core-systems design](06-core-systems-design.md).

- **`SceneFlow` (`core/scene_flow/`):** `go_to(path: String)` that can be awaited. Fade to black on a top `CanvasLayer` (about 0.25 s each way), input blocked during the fade, `change_scene_to_packed`.
- **Display:** stretch `canvas_items` + `expand` at 1152×648 in `project.godot`.
- **Main menu (`ui/main_menu/`):** the main scene. Title, Play, Settings, Quit; Quit hidden on web. Built from Containers + a shared Theme. Settings is a placeholder hook until the settings-panel ticket. Play goes to a stub game scene under `game/` until the example game scene exists.
- **Web start overlay:** "click anywhere to start", web only (`OS.has_feature("web")`); that click calls `Audio.play_music`. Desktop starts the music directly.

Done when the menu → stub game → menu flow works in a headless smoke run, the load check is clean, and a windowed frame capture shows the menu. Handoff names the menu for a visual check.
