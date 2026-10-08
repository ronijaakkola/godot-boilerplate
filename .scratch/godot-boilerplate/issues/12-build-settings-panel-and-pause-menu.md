# Build the settings panel and pause menu

Type: task
Status: open
Blocked by: 10, 11

## Question

AFK build, per the [core-systems design](06-core-systems-design.md).

- **Settings panel (`ui/settings/settings_menu.tscn`):** sliders for Master/Music/SFX and a Reduce motion toggle, bound to `Settings`. Sliders commit on `drag_ended`. The SFX slider plays the demo SFX on `drag_ended`. On open, the panel reads the current values.
- **Pause menu (`ui/pause_menu/`):** Resume, Settings, Main menu. A new `pause` input action (Esc) toggles it via `get_tree().paused`, with the menu's `process_mode = ALWAYS`. Instanced by game scenes (the stub game scene for now), never by the main menu.
- **Wiring:** the main menu's Settings button opens the same panel.

Done when both menus instantiate alone, a test covers pause toggling and settings binding, and a frame capture shows both. Handoff names them for a visual check.

## Comments

- From the Audio and Settings ticket: the SFX slider's demo sound is `shared/audio/ui_click.ogg` via `Audio.play_sfx(...)`. Every assignment to a `Settings` property applies it and saves the file, so assign `Settings.master_volume` / `music_volume` / `sfx_volume` (linear 0–1) only on `drag_ended`, and `reduce_motion` on toggle. For tests, follow the fresh-instance pattern in `test/core/settings/settings_test.gd` so the developer's own `user://settings.cfg` survives.
- From the SceneFlow and main menu ticket:
  - The stub game's "Main menu" button (`game/game.tscn`) is a stand-in: replace it with the pause menu.
  - The main menu's Settings button is already connected to an empty `_on_settings_button_pressed()` in `ui/main_menu/main_menu.gd`.
  - `SceneFlow` processes always, so it works while paused, but it doesn't reset `get_tree().paused`. Going to the main menu from the pause menu has to unpause, either in the pause menu or with one line in `SceneFlow`. Decide here.
  - Call `SceneFlow.go_to(PATH)` without `await`; the menu is freed mid-transition.
  - For click tests, copy `before()`/`after()` and `_click()` from `test/ui/main_menu/main_menu_test.gd` (headless window size and the one-frame layout wait).
