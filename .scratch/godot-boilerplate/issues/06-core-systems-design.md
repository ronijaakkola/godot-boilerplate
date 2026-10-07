# Design the core systems

Type: grilling
Status: resolved
Blocked by: 01, 04

## Question

Decide the shape of each boilerplate system: global signal bus (which signals ship by default, typing), audio controller (buses Master/Music/SFX, music crossfade, SFX API, web audio unlock), scene flow (menu → game, transitions, loading), and settings (which settings exist — volumes, fullscreen, quality?, mouse sensitivity? — and how they persist on web).

Note (from ticket 03): decide whether LimboConsole is available in the itch build. `disable_in_release_build` only hides it — scripts and ~9 MB of fonts still ship.

Note (from ticket 04): autoload names are fixed as `Events`, `Audio`, `SceneFlow`, `Settings`, each in `core/<name>/`. `Events` carries only past-tense broadcast facts (typed, `##`-documented); commands are direct autoload calls, never `*_requested` signals. Autoloads never reach into the current scene.

Note (from ticket 05): measured on the bootstrap export, the web `index.pck` is 7.6 MB, and almost all of it is LimboConsole's Monaspace fonts. `addons/limbo_console.cfg` currently has the defaults: `disable_in_release_build=false`, `custom_theme="res://addons/limbo_console_theme.tres"` (no such file, so the built-in theme is used).

## Answer

- **`Events`:** every game-wide fact lives here. Core systems emit on `Events` and declare no public signals of their own. `events.gd` ships only events that have a listener in the boilerplate: `piece_placed(position: Vector3)` (emitted by the example scene's placement, heard by its HUD count). New events are added when something listens.
- **`Audio`:**
  - **Buses:** `Master`, `Music`, `SFX`. Ambient counts as music, UI as SFX. Default Sample playback, no bus effects.
  - **Music:** `play_music(stream: AudioStream, fade := 1.0)` crossfades between two internal players, one track at a time. Asking for the track already playing does nothing. `stop_music(fade := 1.0)` fades out.
  - **SFX:** `play_sfx(stream: AudioStream, pitch_jitter := 0.0)` on a pool of about 8 non-positional players, round robin. Callers `preload` their own streams; there is no registry.
  - **While paused:** `Audio` processes always, so music continues during pause with no ducking.
  - **Verified in source (Sample mode):** bus volume and mute apply live, and a Tween on `volume_db` works.
- **Web audio unlock:** on web only, the main menu shows a "click anywhere to start" overlay, and that click starts the menu music. Desktop goes straight to the menu. Drop the overlay if the browser test shows itch's own Click to Play is enough.
- **`SceneFlow`:**
  - `go_to(path: String)`. Callers hold a `const` path; `PackedScene` would create cyclic preloads (menu ↔ game).
  - Uses `change_scene_to_packed`, so `current_scene` stays standard and F6 works.
  - One transition: a fade to black on a top `CanvasLayer`, about 0.25 s out, swap, about 0.25 s in. Input is blocked while fading, and `go_to` can be awaited. It may be replaced with something more thematic during the jam.
  - **Loading:** a normal load while the screen is black, with no loading screen. On the no-threads web build, `load_threaded_request` runs synchronously on the calling thread, so a progress bar would jump straight from 0 to 1.
- **`Settings`:**
  - Typed properties: `master_volume`, `music_volume`, `sfx_volume` (linear 0–1; defaults 0.8 / 0.6 / 0.8) and `reduce_motion: bool` (default off). It covers motion and flashes only, not graphics quality.
  - Each setter applies the value (bus volumes via `AudioServer` + `linear_to_db`), saves `user://settings.cfg` (`ConfigFile`) and closes it.
  - Saves happen on every committed change: toggles immediately, sliders on `drag_ended`. Loaded and applied in `_ready()`. If storage isn't persistent, settings quietly last for the session only.
  - Consumers read a setting when they use it, so there is no `setting_changed` event.
  - Settings are player preferences only, never game progress (see `CONTEXT.md`).
- **Settings left out:** fullscreen (itch's embed fullscreen button covers it; ticket 08 turns it on) and mouse sensitivity (add during the jam if playtesters ask). Graphics quality waits for the soft-look prototype.
- **Display:** stretch mode `canvas_items`, aspect `expand`, base 1152×648. UI scales in fullscreen, and mouse-motion `relative` is in content units, so drags feel the same windowed and fullscreen. With stretch `disabled` (the old default), fullscreen left the UI small and changed drag feel.
- **UI scenes:**
  - **Main menu:** the project's main scene. Title, Play, Settings, Quit (Quit hidden on web). No credits screen and no custom splash.
  - **Settings panel:** `ui/settings/settings_menu.tscn`, instanced by both the main menu and the pause menu. The SFX slider plays a demo sound on `drag_ended`.
  - **Pause menu:** `ui/pause_menu/`, instanced by each game scene, not an autoload. A new `pause` input action (Esc) toggles it, using `get_tree().paused` with the menu's `process_mode = ALWAYS`.
- **Placeholder audio:** CC0 menu music loop, UI SFX and placement SFX in `shared/audio/`, with sources and licenses in `CREDITS.md`. They're replaced on jam day. No sound plays automatically on every button press.
- **LimboConsole:** stays out of the itch build.
  - Add `addons/limbo_console/*, addons/limbo_console.cfg` to the Web `exclude_filter`, which takes the `.pck` from 7.6 MB to about 6 KB. Startup logs one "Failed to instantiate an autoload" error line, which is accepted. The cleaner fix if that line bothers anyone is a small EditorExportPlugin that drops the autoload for `web` exports (tested).
  - Any script that names `LimboConsole` fails to compile on web, so all our console commands live in `core/dev_console/dev_commands.gd`. It's loaded only when `get_tree().root.get_node_or_null(^"LimboConsole")` exists, and is excluded from the Web preset too.
  - It ships one example command: `goto <scene path>`, which calls `SceneFlow.go_to`.
  - Feature-tag autoload overrides don't work, and `disable_in_release_build` saves nothing.
- **Fullscreen, for reference:** `window_set_mode(FULLSCREEN)` from a `Button` press works on web (it runs inside the browser's mouse event), but key-triggered requests are deferred. The mode reads back a frame late, and leaving with Esc has no signal. Moot now that the setting is dropped.
