# Map: Godot jam boilerplate

Label: wayfinder:map

## Destination

A Godot 4.7 GDScript project the team clones on jam day (November 2026): web export running on itch.io, agent guidelines and Godot skills, lint-on-edit, tests in CI on PRs, auto-deploy to itch.io from `main`, and global signals, audio, scene flow, main menu with settings, and one example game scene already built.

## Notes

- **Execution override:** this map carries execution, not just planning. Tickets may be decisions *or* builds; a build ticket follows once a piece has nothing left to decide. Build incrementally before November.
- **Game context** (idea not set): cosy, possibly puzzle, **3D** with a soft/cute shader look; played mostly with the **mouse**; player probably places/moves pieces on the ground; daily runs + designed levels likely; audio is ambient music + SFX only (no adaptive/positional).
- **Fixed constraints:** Godot **4.7.2** (pinned for the whole team), **GDScript** only, **web (itch.io) first** — desktop builds are a bonus. **Web always wins** over visual ambition: the look is tuned to the Compatibility renderer.
- **Workflow:** everyone uses Claude Code (`CLAUDE.md` + `.claude/skills/`). Agent-first, but editor/manual work must stay first-class — headless is supported, never required.
- **Automation split:** local = lint only (Claude Code hook + git pre-commit); PRs = full test suite in CI; push to `main` = deploy web build to itch.io.
- **Tooling picks:** gdUnit4 (tests), LimboConsole (dev console), gdtoolkit (`gdlint`/`gdformat`); plugins vendored under `addons/` with pinned versions. GitHub hosting.
- **Skills every session should consult:** `/grilling` + `/domain-modeling` for grilling tickets; `/research` for research tickets; `/writing-for-agents` when writing `CLAUDE.md` or skills; `/tdd` for build tickets with logic.
- Research findings live in `research/` next to this map (no research branches — the repo had no commits when charted).

## Decisions so far

<!-- one line per closed ticket: [title](issues/NN-slug.md) — gist -->

- [What can Godot 4.7's Compatibility renderer do for a soft 3D look on the web, and what are the itch.io web export gotchas?](issues/01-web-renderer-and-export-limits.md) — Compatibility/WebGL2 only (no WebGPU); soft look via glow, depth fog, simplified SSAO, AgX + LUT, toon `light()`, baked lightmaps (bake needs a GPU, not CI); no-threads export; save on every change; music starts on the title-screen click.
- [What can agents do with headless Godot alone, and which Godot MCP server (if any) fills the gaps?](issues/02-headless-godot-and-mcp.md) — headless covers import, compile check, smoke runs, gdUnit4 and web export, but bare `--check-only` is unreliable (macOS always exits 0, autoloads break it) so use a `load()`-every-script check, and grep logs for runtime `ERROR`; no MCP required; optional candidate hi-godot/godot-ai needs a trial; visual checks stay human.
- [Are gdUnit4, LimboConsole and gdtoolkit compatible with 4.7, and what's the GitHub Actions setup for Godot tests plus butler deploy?](issues/03-plugins-and-ci-compat.md) — pin gdUnit4 v6.2.1, LimboConsole v0.8.0, gdtoolkit 4.5.0 (all clean on local 4.7.2); hooks run `gdlint` + `gdformat --check` only (gdformat can break code); CI via setup-godot v2.4.3 + gdUnit4-action v1.3.2; deploy with pinned butler 15.32.0, secret `BUTLER_API_KEY`, var `ITCH_TARGET`, channel `html5`.
- [Folder layout and architecture conventions](issues/04-folder-layout-and-conventions.md) — by-feature layout (`core/ ui/ game/ shared/ test/`); Godot style guide, `class_name` only when referenced, untyped declarations are errors; autoloads `Events`/`Audio`/`SceneFlow`/`Settings`; call down, signal up, and every scene instantiates alone; facts on the bus, commands as autoload calls; agents may hand-edit any `.tscn` but self-check visuals by frame capture; one person per scene, take one side on conflicts; `.glb` only, no LFS.
- [Bootstrap the project](issues/05-bootstrap-project.md) — 4.7.2 Compatibility project with vendored gdUnit4 6.2.1 + LimboConsole 0.8.0 (enabled headlessly, autoload + input actions + cfg), `untyped_declaration` as Error (addons excluded by 4.7's default `directory_rules`), no-threads `Web` preset excluding tests, `gdlintrc` skipping `addons/`, README setup; import and web export pass locally (pck 7.6 MB, nearly all console fonts).

## Not yet specified

- **Building each core system**: signal bus, audio controller, scene flow, main menu + settings UI. Graduates into build tickets once the core-systems design ticket resolves.
- **Soft-look baseline**: a prototype of the WorldEnvironment, lighting and toon/soft shader that works in Compatibility on the web. Renderer research done; still unverified in a browser: stencil outlines on WebGL2, audio unlock via itch's "Click to Play", saves inside itch's iframe across Safari/Chrome storage partitioning.
- **Example game scene**: camera, lighting, the soft-look environment, and click-to-place a cube on a ground plane (3D mouse picking). A pattern for agents to copy, replaced on jam day. Hangs on the conventions and core-systems designs.
- **Which tests the boilerplate itself ships with**: what's covered, and which tests are examples for agents to copy.
- **Dialogue plugin**: possibly in scope later, but only if the game idea needs it. Revisit after the jam theme.

## Out of scope

- Game-specific systems: daily runs / seeded RNG, designed-level format, piece placement mechanics, dialogue — they depend on the unset game idea; built during the jam, not in the boilerplate.
- Desktop-specific work (builds may work, not a deal breaker).
- Reuse as a general template for future jams — this boilerplate targets this jam only.
