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
- **Tooling picks:** gdUnit4 (tests), LimboConsole (dev console), gdtoolkit (`gdlint` only; `gdformat` dropped in Agent guidance); plugins vendored under `addons/` with pinned versions. GitHub hosting.
- **Skills every session should consult:** `/grilling` + `/domain-modeling` for grilling tickets; `/research` for research tickets; `/writing-for-agents` when writing `CLAUDE.md` or skills; `/tdd` for build tickets with logic.
- Research findings live in `research/` next to this map (no research branches — the repo had no commits when charted).

## Decisions so far

<!-- one line per closed ticket: [title](issues/NN-slug.md) — gist -->

- [What can Godot 4.7's Compatibility renderer do for a soft 3D look on the web, and what are the itch.io web export gotchas?](issues/01-web-renderer-and-export-limits.md) — Compatibility/WebGL2 only (no WebGPU); soft look via glow, depth fog, simplified SSAO, AgX + LUT, toon `light()`, baked lightmaps (bake needs a GPU, not CI); no-threads export; save on every change; music starts on the title-screen click.
- [What can agents do with headless Godot alone, and which Godot MCP server (if any) fills the gaps?](issues/02-headless-godot-and-mcp.md) — headless covers import, compile check, smoke runs, gdUnit4 and web export, but bare `--check-only` is unreliable (macOS always exits 0, autoloads break it) so use a `load()`-every-script check, and grep logs for runtime `ERROR`; no MCP required; optional candidate hi-godot/godot-ai needs a trial; visual checks stay human.
- [Are gdUnit4, LimboConsole and gdtoolkit compatible with 4.7, and what's the GitHub Actions setup for Godot tests plus butler deploy?](issues/03-plugins-and-ci-compat.md) — pin gdUnit4 v6.2.1, LimboConsole v0.8.0, gdtoolkit 4.5.0 (all clean on local 4.7.2); hooks run `gdlint` + `gdformat --check` only (gdformat can break code); CI via setup-godot v2.4.3 + gdUnit4-action v1.3.2; deploy with pinned butler 15.32.0, secret `BUTLER_API_KEY`, var `ITCH_TARGET`, channel `html5`.
- [Folder layout and architecture conventions](issues/04-folder-layout-and-conventions.md) — by-feature layout (`core/ ui/ game/ shared/ test/`); Godot style guide, `class_name` only when referenced, untyped declarations are errors; autoloads `Events`/`Audio`/`SceneFlow`/`Settings`; call down, signal up, and every scene instantiates alone; facts on the bus, commands as autoload calls; agents may hand-edit any `.tscn` but self-check visuals by frame capture; one person per scene, take one side on conflicts; `.glb` only, no LFS.
- [Bootstrap the project](issues/05-bootstrap-project.md) — 4.7.2 Compatibility project with vendored gdUnit4 6.2.1 + LimboConsole 0.8.0 (enabled headlessly, autoload + input actions + cfg), `untyped_declaration` as Error (addons excluded by 4.7's default `directory_rules`), no-threads `Web` preset excluding tests, `gdlintrc` skipping `addons/`, README setup; import and web export pass locally (pck 7.6 MB, nearly all console fonts).
- [Design the core systems](issues/06-core-systems-design.md) — all game-wide facts on `Events` (ships `piece_placed` only); `Audio` with Master/Music/SFX buses, one crossfaded music track and a pooled `play_sfx(stream)`; `SceneFlow.go_to(path)` with a fade and no loading screen; typed `Settings` (3 volumes + reduce motion) saved on each change; web-only click-to-start overlay; shared settings panel + per-scene pause menu; stretch `canvas_items`/`expand`, no fullscreen or sensitivity setting; LimboConsole excluded from the web build, commands only in one guarded script.
- [Agent guidance](issues/07-agent-guidance.md) — a cross-platform `uv run tools/check.py` wrapper (`lint`/`load`/`test`/`smoke`/`capture`/`all`) owns every Godot flag; gdlint only, gdformat dropped; committed Claude Code lint hook + pre-commit lint; short Godot-only `CLAUDE.md` pointing to `CODING_STANDARDS.md`, `DESIGN.md`, `CONTEXT.md`, `docs/web-constraints.md`; two skills (`gdunit-tests`, `edit-tscn`); no MCP, no third-party skill packs; personal setups stay personal.
- [Set up the itch.io project and butler API key in GitHub secrets](issues/08-itch-and-secrets-setup.md) — public repo `ronijaakkola/godot-boilerplate`; draft itch HTML page `nashtanir/game-off-2026` with the fullscreen button on; `BUTLER_API_KEY` secret and `ITCH_TARGET` variable set; channel `html5`.
- [Build the CI pipeline](issues/09-ci-pipeline.md) — PRs run gdUnit4 via gdUnit4-action (empty `test/` passes); pushes to `main` export Web and butler-push to `nashtanir/game-off-2026:html5`, live and playable; `test` is a required check with admins exempt so direct pushes still work; `build/*` excluded from the export.
- [Build the agent guidance](issues/14-build-agent-guidance.md) — `uv run tools/check.py` (`lint`/`load`/`test`/`smoke`/`capture`/`all`) verified on the Mac: `load` also loads scenes and resources, every Godot step imports first, `smoke` waits for a main scene; lint hook and pre-commit lint work end-to-end; CI `checks` job required on `main`; `CLAUDE.md`, `CODING_STANDARDS.md`, `DESIGN.md`, `docs/web-constraints.md` and two skills shipped. Windows run split out.

## Not yet specified

- **Soft-look baseline**: a prototype of the WorldEnvironment, lighting and toon/soft shader that works in Compatibility on the web. Renderer research done; still unverified in a browser: stencil outlines on WebGL2, audio unlock via itch's "Click to Play", saves inside itch's iframe across Safari/Chrome storage partitioning. Also: whether to cap the 3D render scale in fullscreen, since `canvas_items` stretch renders 3D at full screen resolution (costly on HiDPI laptops in Compatibility).
- **Example game scene**: camera, lighting, the soft-look environment, and click-to-place a cube on a ground plane (3D mouse picking). A pattern for agents to copy, replaced on jam day. Known pieces: emits `Events.piece_placed`, a HUD placed-count label listens; a small camera shake on placement, skipped when `Settings.reduce_motion` is on; plays the placement SFX; instances the pause menu. Open: does the camera orbit on right-drag?
- **Which tests the boilerplate itself ships with**: what's covered, and which tests are examples for agents to copy.
- **Jam-day handoff cleanup**: before the team clones it, strip the map and the issue-tracker / triage / domain-docs sections from `CLAUDE.md`, and decide what happens to `.scratch/` and `docs/agents/` (`docs/web-constraints.md` links to the renderer research in `.scratch/`). Also the merge flow for teammates: `test` is required on `main` and only admins bypass it, so the CLAUDE.md rule "local `git merge --squash`, then push" won't work for the team. They'd use GitHub's "Squash and merge" instead. Consider disabling merge commits in the repo settings, since PR #1 landed as a merge commit.
- **Dialogue plugin**: possibly in scope later, but only if the game idea needs it. Revisit after the jam theme.

## Out of scope

- Game-specific systems: daily runs / seeded RNG, designed-level format, piece placement mechanics, dialogue — they depend on the unset game idea; built during the jam, not in the boilerplate.
- Desktop-specific work (builds may work, not a deal breaker).
- A Godot MCP (godot-ai or another): headless checks plus frame capture cover the agent loop, and an MCP adds an install step for everyone. Not trialled in this effort ([Agent guidance](issues/07-agent-guidance.md)).
- Reuse as a general template for future jams — this boilerplate targets this jam only.
