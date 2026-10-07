# Design the core systems

Type: grilling
Status: open
Blocked by: 01, 04

## Question

Decide the shape of each boilerplate system: global signal bus (which signals ship by default, typing), audio controller (buses Master/Music/SFX, music crossfade, SFX API, web audio unlock), scene flow (menu → game, transitions, loading), and settings (which settings exist — volumes, fullscreen, quality?, mouse sensitivity? — and how they persist on web).

Note (from ticket 03): decide whether LimboConsole is available in the itch build. `disable_in_release_build` only hides it — scripts and ~9 MB of fonts still ship.

Note (from ticket 04): autoload names are fixed as `Events`, `Audio`, `SceneFlow`, `Settings`, each in `core/<name>/`. `Events` carries only past-tense broadcast facts (typed, `##`-documented); commands are direct autoload calls, never `*_requested` signals. Autoloads never reach into the current scene.

Note (from ticket 05): measured on the bootstrap export, the web `index.pck` is 7.6 MB, and almost all of it is LimboConsole's Monaspace fonts. `addons/limbo_console.cfg` currently has the defaults: `disable_in_release_build=false`, `custom_theme="res://addons/limbo_console_theme.tres"` (no such file, so the built-in theme is used).
