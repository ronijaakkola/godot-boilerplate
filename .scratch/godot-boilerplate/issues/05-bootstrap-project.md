# Bootstrap the project

Type: task
Status: resolved
Blocked by: 03, 04

## Question

Create the Godot 4.7.2 project skeleton per the conventions decision: `project.godot` using the Compatibility renderer, web export preset (threads setting per research), vendored gdUnit4 + LimboConsole under `addons/` at pinned versions, gdtoolkit config, `.gitignore`/`.gitattributes` for Godot, and the folder layout. AFK. Done when the project opens headlessly without errors and exports to web locally.

Note (from ticket 01): the local machine has 4.7.1 export templates but editor 4.7.2 — web export fails until the exact 4.7.2 Web templates (`web_nothreads_release.zip`) are installed. Bootstrap docs must tell every teammate to install them.

Note (from ticket 04): create the folders `core/ ui/ game/ shared/ test/`; set the `untyped_declaration` warning to Error in `project.godot`; use Godot's generated `.gitattributes`/`.gitignore` (no `merge=binary`, no LFS); the Web preset's `exclude_filter` covers `addons/gdUnit4/*, test/*`.

## Answer

Done, uncommitted in the working tree. What exists now:

- **`project.godot`**: name "Godot Jam Boilerplate", features `4.7` + `GL Compatibility`, `rendering_method` and `.mobile` both `gl_compatibility`, `debug/gdscript/warnings/untyped_declaration=2` (Error). Both plugins listed under `[editor_plugins]`. No main scene and no icon yet; scenes belong to the build tickets.
- **Warnings and addons**: in 4.7 `exclude_addons` is gone. The default `debug/gdscript/warnings/directory_rules` is `{"res://addons": EXCLUDE}`, so the Error setting doesn't hit vendored code, and gdUnit4's `inferred_declaration` guard passes. Don't override `directory_rules` without keeping that entry.
- **Plugins**: gdUnit4 v6.2.1 (tag SHA `08ffc7c…` verified, `test/` removed, 1.7 MB) and LimboConsole v0.8.0 (SHA `969f5d4…` verified, 9.0 MB). The first import generated `.uid` files for gdUnit4 and `.import` files for LimboConsole's fonts. Commit them.
- **LimboConsole enable without the editor**: a one-off headless `-s` script mirrored `plugin.gd` `_enable_plugin()`. It added the `LimboConsole` autoload and the input actions `limbo_console_toggle` (backtick), `limbo_auto_complete_reverse` (Shift+Tab) and `limbo_console_search_history` (Ctrl+R) via `ProjectSettings.save()`, and wrote `addons/limbo_console.cfg` through the plugin's own `ConfigMapper` (defaults, so `disable_in_release_build=false`). The script isn't kept; the result is identical to an editor toggle.
- **`export_presets.cfg`**: preset `Web`, `export_path="build/web/index.html"`, `exclude_filter="addons/gdUnit4/*, test/*"`, `variant/thread_support=false`, `variant/extensions_support=false`, `progressive_web_app/enabled=false`. Other options are left at their defaults.
- **`gdlintrc`**: gdtoolkit 4.5.0 defaults plus `.godot` and `addons` in `excluded_directories`. No `gdformatrc`, because the defaults (tabs, 100 columns) match gdlint. Still, hooks must filter `addons/` themselves when they pass explicit files (#395).
- **`.gitignore`** (Godot's generated `.godot/` and `/android/`, plus `reports/` and `build/`) and **`.gitattributes`** (`* text=auto eol=lf`).
- **Folders** `core/ ui/ game/ shared/ test/`, each with a `.gitkeep`.
- **`README.md`**: setup (Godot 4.7.2, the 4.7.2 Web templates via Editor → Manage Export Templates, uv, `git config core.hooksPath .githooks`), the layout table, the pinned versions and the headless commands.

Verified on macOS with 4.7.2:
- `--import`: exit 0, no errors or warnings.
- `--export-release "Web"`: exit 0. `index.wasm` is 39.5 MB, `index.pck` 7.6 MB, and the pck is almost all LimboConsole fonts.
- The pck holds no gdUnit4 files; the only mention is the `editor_plugins` entry in project settings.
- A `-s` check confirms the `LimboConsole` autoload resolves.
- `gdlint .` skips `addons/` and flags a bad name in `core/`.

Local machine: the 4.7.2 `web_nothreads_{debug,release}.zip` and `version.txt` were installed into `~/Library/Application Support/Godot/export_templates/4.7.2.stable/`. They were pulled out of the official `.tpz` with HTTP range reads, not the full 1.28 GB download.
