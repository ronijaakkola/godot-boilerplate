# Godot Jam Boilerplate

Godot 4.7.2 GDScript project, web (itch.io) first, Compatibility renderer.

## Setup

1. Install **Godot 4.7.2** exactly. The whole team and CI are pinned to it.
2. Install the **4.7.2 Web export templates**. In the editor: **Editor → Manage Export Templates…**, download only the Web templates. Templates from another version (even 4.7.1) fail with "No export template found".
3. Install [uv](https://docs.astral.sh/uv/). The lint tools run through `uvx`, so nothing else is needed.
4. Enable the git hooks once per clone: `git config core.hooksPath .githooks`.
5. Open the project in the editor once, or run `godot --headless --path . --import`.

## Layout

| Folder | What goes there |
|---|---|
| `addons/` | Vendored plugins at pinned versions. Never hand-edited. |
| `core/<system>/` | One folder per autoload. |
| `ui/` | Main menu, settings screen, Theme, shared widgets. |
| `game/` | The example game scene, replaced on jam day. |
| `shared/` | Assets used by more than one feature. |
| `test/` | gdUnit4 tests, mirroring the `res://` path of what they test. |

## Pinned versions

| Tool | Version |
|---|---|
| Godot | 4.7.2 |
| gdUnit4 | 6.2.1 (`addons/gdUnit4/`) |
| LimboConsole | 0.8.0 (`addons/limbo_console/`) |
| gdtoolkit | 4.5.0 (`uvx --from gdtoolkit==4.5.0`) |

## Commands

```sh
godot --headless --path . --import                                         # import assets
uvx --from gdtoolkit==4.5.0 gdlint .                                       # lint (skips addons/)
mkdir -p build/web && godot --headless --path . --export-release "Web" build/web/index.html
```
