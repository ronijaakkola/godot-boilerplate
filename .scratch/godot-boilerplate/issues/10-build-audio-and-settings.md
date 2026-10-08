# Build the Audio and Settings core systems

Type: task
Status: resolved
Blocked by: 06, 14

## Question

AFK build, per the [core-systems design](06-core-systems-design.md). Use `/tdd` for the logic.

- **Autoloads:** `Events` (`core/events/events.gd`, `piece_placed` only, plus the `##` doc format), `Audio` (`core/audio/`) and `Settings` (`core/settings/`), registered in `project.godot`.
- **Buses:** a `Master`/`Music`/`SFX` bus layout.
- **`Audio`:** `play_music` / `stop_music` with a two-player crossfade, and `play_sfx` on a pool of about 8 players with `pitch_jitter`. It processes always.
- **`Settings`:** typed `master_volume` / `music_volume` / `sfx_volume` / `reduce_motion` with defaults 0.8 / 0.6 / 0.8 / off. Setters apply the value and save `user://settings.cfg`, which is loaded and applied in `_ready()`.
- **Placeholder audio:** CC0 menu loop, UI SFX and placement SFX in `shared/audio/`, with `CREDITS.md`.
- **Tests:** gdUnit4 tests for `Settings` (defaults, round-trip through the cfg, bus volume applied) and `Audio` (same track doesn't restart, pool round robin).

Done when `uv run tools/check.py all` passes.

Note (from ticket 07): built by an agent working under the new guidance (`CLAUDE.md`, `CODING_STANDARDS.md`, the skills). Note any gap or wrong instruction in the guidance as a comment here, so the guidance gets tested in use.

## Answer

Built and green: `uv run tools/check.py all` passes (lint, load 6 files, 6 tests). `smoke` is skipped until ticket 11 sets a main scene. The tests boot the autoloads, so they're the check that catches a broken one.

- **Autoloads** (registered after `LimboConsole`): `Events` (`core/events/events.gd`), `Audio` (`core/audio/audio.gd`), `Settings` (`core/settings/settings.gd`). None has a `class_name`.
- **Buses:** `Master`, `Music`, `SFX` in `core/audio/default_bus_layout.tres`, set as `audio/buses/default_bus_layout` in `project.godot`.
- **`Events`:** `piece_placed(position: Vector3)`. The file opens with `@warning_ignore_start("unused_signal")`, since a bus event is never emitted in `events.gd` and Godot 4.7 warns on every one of them (verified by raising the warning to Error).
- **`Audio`:**
  - `play_music(stream: AudioStream, fade := 1.0)`: crossfades over two players and does nothing when asked for the current track.
  - `stop_music(fade := 1.0)`.
  - `play_sfx(stream: AudioStream, pitch_jitter := 0.0)`: 8 pooled players, round robin, so the oldest sound gets cut off.
  - It sets `process_mode = ALWAYS` itself. A newer fade kills the older tween on the same player, so a stale fade-out can't stop a restarted track.
- **`Settings`:** `master_volume`, `music_volume`, `sfx_volume` (linear 0 to 1) and `reduce_motion`. Each setter applies the value (`AudioServer.set_bus_volume_linear`) and saves the whole file. The file is `user://settings.cfg`, section `[settings]`, keys named like the properties. `_ready()` loads the file and assigns every key, defaults included, so the bus volumes apply even with no file. It also guards against saving during that load.
- **Placeholder audio** in `shared/audio/`, named by role so jam day can swap a file in under the same name: `menu_music.ogg` (Heavenly Loop by isaiah658, 34 s, 1.2 MB, `loop=true` in its `.import`), `ui_click.ogg` (Kenney Interface Sounds) and `piece_placed.ogg` (Kenney Impact Sounds). All are CC0, with sources in `CREDITS.md`.
- **Tests:**
  - `test/core/settings/settings_test.gd`: defaults with no file, defaults reach the buses, changes last into a new session, a volume change reaches its bus.
  - `test/core/audio/audio_test.gd`: the same track keeps playing, and the ninth SFX takes the oldest player.
  - Both test fresh instances of the scripts, not the live autoloads.

## Comments

- **Guidance in use:**
  - **`gdunit-tests` skill:** it said to delete `user://settings.cfg` in `after_test()`, which wipes the developer's own settings on every `check.py test`. Fixed: the skill now points to the fresh-instance pattern in `settings_test.gd`, where the file is deleted before each test and the live `Settings` values are written back in `after()`.
  - **`CODING_STANDARDS.md`:** its bus event example doesn't mention the `unused_signal` warning. `events.gd` handles it once for the whole file, so nothing else needs it. No change.
  - **`check.py`:** the load check doesn't surface GDScript warnings, only errors. Fine for now; noted in case warnings start mattering.
  - **Otherwise** `CLAUDE.md`, `CODING_STANDARDS.md` and the `check.py` table were enough to work from.
- **For ticket 11:** the web start overlay calls `Audio.play_music(preload("res://shared/audio/menu_music.ogg"))`.
- **For ticket 12:** the SFX slider's demo sound is `shared/audio/ui_click.ogg`. Sliders assign `Settings.<name>_volume` on `drag_ended`, since every assignment saves.
