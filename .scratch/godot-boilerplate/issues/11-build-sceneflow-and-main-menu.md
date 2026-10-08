# Build SceneFlow and the main menu

Type: task
Status: resolved
Blocked by: 10

## Question

AFK build, per the [core-systems design](06-core-systems-design.md).

- **`SceneFlow` (`core/scene_flow/`):** `go_to(path: String)` that can be awaited. Fade to black on a top `CanvasLayer` (about 0.25 s each way), input blocked during the fade, `change_scene_to_packed`.
- **Display:** stretch `canvas_items` + `expand` at 1152×648 in `project.godot`.
- **Main menu (`ui/main_menu/`):** the main scene. Title, Play, Settings, Quit; Quit hidden on web. Built from Containers + a shared Theme. Settings is a placeholder hook until the settings-panel ticket. Play goes to a stub game scene under `game/` until the example game scene exists.
- **Web start overlay:** "click anywhere to start", web only (`OS.has_feature("web")`); that click calls `Audio.play_music`. Desktop starts the music directly.

Done when the menu → stub game → menu flow works in a headless smoke run, the load check is clean, and a windowed frame capture shows the menu. Handoff names the menu for a visual check.

## Answer

Built and green: `uv run tools/check.py all` passes (lint, load 14 files, 11 tests, smoke of the main menu), and `smoke res://game/game.tscn` passes too. The capture shows the menu. A local Web export succeeds (`.pck` 8.9 MB, still carrying LimboConsole until ticket 13).

- **`SceneFlow`** (`core/scene_flow/scene_flow.gd`, autoloaded after `Settings`): a `CanvasLayer` on layer 128 that builds its black `ColorRect` in code (`mouse_filter` ignore). `go_to(path)` disables the root viewport's input, tweens to black over 0.25 s, calls `change_scene_to_packed(load(path))`, awaits `SceneTree.scene_changed`, tweens back and re-enables input. A call during a transition is ignored. If the change fails, it logs an error and fades back in. It processes always, so a paused scene can leave. It does **not** unpause the tree.
- **Callers fire and forget.** Buttons call `SceneFlow.go_to(PATH)` without `await`, because the calling scene is freed mid-transition. Only tests await it.
- **Display:** `window/stretch/mode="canvas_items"` and `aspect="expand"` in `project.godot`. 1152×648 is Godot's default viewport size, so it isn't written.
- **Main menu** (`ui/main_menu/`, the main scene): title, Play, Settings, Quit, from Containers under `ui/theme.tres`. The theme sets font size 24, a `TitleLabel` type variation at 64, and `VBoxContainer` separation 12. Quit is hidden on web. Settings is connected to an empty `_on_settings_button_pressed()` for ticket 12 to fill in.
- **Web start overlay:** a `StartOverlay` `ColorRect`, hidden by default and shown on web until the first click. The click calls `Audio.play_music(MUSIC)`. A `static var _music_started` survives scene changes, so coming back to the menu doesn't ask again; every later visit just calls `play_music` with the same track, which does nothing. Desktop starts the music in `_ready()`. **Not seen in a browser yet.**
- **Stub game** (`game/game.tscn`, a `Control`): a label and a "Main menu" button. Play goes to `res://game/game.tscn`, so the example game scene should replace the stub at that path.
- **Tests:**
  - `test/core/scene_flow/scene_flow_test.gd`: the scene changes, input is off only while fading, and a second call is ignored.
  - `test/ui/main_menu/main_menu_test.gd`: Play → game → Main menu, and a click on the overlay starts the music.
  - "The flow works in a headless smoke run" is read as this gdUnit test, plus `smoke` for each scene. `smoke` itself only boots one scene and clicks nothing.

## Comments

- From the Audio and Settings ticket: the web start overlay (and desktop boot) calls `Audio.play_music(preload("res://shared/audio/menu_music.ogg"))`. The track is set to loop in its `.import`. Setting a main scene turns `check.py smoke` on; until then the `test` run is the only check that boots the autoloads.
- **Found while building:**
  - **Godot 4.7.2 leaks a playing Ogg at quit.** A bare `AudioStreamPlayer` playing `menu_music.ogg` logs `ERROR: 2 resources still in use at exit` when the process quits, headless or windowed. Stopping it about 20 frames earlier avoids the error; stopping it in the last frame doesn't. `--quit-after` gives our code no hook, so `check.py` now drops that one line before looking for errors in `smoke` and `capture` (`EXIT_LEAK`). A desktop Quit logs it too, which is harmless.
  - **Headless clicks and the stretch mode.** Headless, the root window is 64×64, so `canvas_items` stretch scales gdUnit's simulated mouse positions by 18 and every click missed. `main_menu_test.gd` sets `get_tree().root.size` to 1152×648 in `before()` and restores it in `after()`. Containers also place their children a frame after entering the tree, so a test waits one frame before reading a button's rect. The `gdunit-tests` skill now says both. The fix lives in the tests, not in `check.py`, because CI runs gdUnit4-action directly.
