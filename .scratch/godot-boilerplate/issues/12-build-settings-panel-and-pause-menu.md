# Build the settings panel and pause menu

Type: task
Status: resolved
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

## Answer

Built in `feat(ui): add the settings panel and pause menu` (8f6ea28). `check.py all` passes: 20 tests, smoke on the main menu and `game/game.tscn`.

- **Settings panel** (`ui/settings/settings_menu.tscn`): a full-screen dim plus a centred panel with Master / Music / Sound effects sliders (0–1, step 0.01), a Reduce motion `CheckButton` and Back. `open()` reads the current `Settings` values and shows the panel (it also reads them at `_ready`, so F6 shows real values). Back hides it. The parents only call `open()`, so the panel has no signals.
- **Slider commits:** a drag commits on `drag_ended`, and the SFX slider plays `ui_click.ogg` then. A change that isn't a drag (mouse wheel, arrow keys, the click that starts a drag) commits at once, so the setting never lags behind the slider. `drag_ended`'s `value_changed` flag is ignored: a plain click on the track reports `false` though it moved the value.
- **Pause menu** (`ui/pause_menu/pause_menu.tscn`): a `CanvasLayer` root on layer 10 with `process_mode = ALWAYS`. A CanvasLayer draws over the game's own UI wherever it sits in a game scene, and works under a `Node3D` root. Resume / Settings / Main menu. The `pause` action (Esc) toggles it in `_unhandled_input`. `open()` pauses and `close()` unpauses. Resume or Esc also closes the settings panel if it's open on top.
- **Unpause decision:** `SceneFlow.go_to` sets `get_tree().paused = false` after the fade to black, before the scene change. Any future caller (game over, level select) gets an unpaused scene, and the paused game doesn't move during the fade-out.
- **Instancing:** parents hide the instance (`visible = false` on the instancing node), never the sub-scene's own root, so both scenes capture and F6 visible on their own. The stub game drops its Main menu button and `game.gd` and instances the pause menu. The main menu's Settings button opens the shared panel.
- **Tests:** `test/ui/settings/settings_menu_test.gd` (5: open reads values, a drag commits only when it ends, a non-drag change commits at once, the toggle, Back) restores the live `Settings` values in `after()`. `test/ui/pause_menu/pause_menu_test.gd` (2: Esc opens and closes, Resume closes the panel too). Added: the main menu's Settings button opens the panel, and SceneFlow unpauses.
- **gdUnit trap, added to the `gdunit-tests` skill:** the runner's `simulate_key_pressed` / `simulate_action_pressed` deliver the event twice to the root's `_unhandled_input` (viewport, then a direct call), so a toggle flips back. The pause test sends Esc through `Input.parse_input_event` alone.
- **Unverified in a browser:** in browser fullscreen, Esc leaves fullscreen and doesn't reach the game, so the first Esc there won't pause.
- **Needs a visual check:** `ui/settings/settings_menu.tscn`, `ui/pause_menu/pause_menu.tscn`.
