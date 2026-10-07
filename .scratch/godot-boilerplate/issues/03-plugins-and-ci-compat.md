# Are gdUnit4, LimboConsole and gdtoolkit compatible with 4.7, and what's the GitHub Actions setup for Godot tests plus butler deploy?

Type: research
Status: resolved
Blocked by:

## Question

- gdUnit4: latest release supporting Godot 4.7.2, install as vendored addon, headless CLI invocation, report formats, official GitHub Action.
- LimboConsole: latest release supporting 4.7, how to register commands, can it be stripped/disabled in release web builds.
- gdtoolkit (`gdlint`/`gdformat`): version supporting Godot 4.x GDScript syntax (incl. any 4.5+ syntax like abstract classes/variadic args), config file format, known false positives.
- GitHub Actions: maintained ways to install Godot 4.7.2 + export templates in CI (e.g. chickensoft-games/setup-godot, barichello/godot-ci, raw download), headless test run, web export, and deploying to itch.io via butler (action or CLI, required secrets, channel naming).

## Answer

- **gdUnit4 `v6.2.1`** (vendored from the source tag, without `addons/gdUnit4/test/`): upstream lists support up to 4.7.1. It imported and ran tests cleanly on local 4.7.2. Local headless runs need `--ignoreHeadlessMode`. Exit codes are 0/100/101, and reports come out as HTML plus JUnit XML. In CI, use `godot-gdunit-labs/gdUnit4-action@v1.3.2` with `version: installed`. It downloads Godot itself and runs under xvfb, not headless.
- **LimboConsole `v0.8.0`**: no stated 4.7 support, but it loaded and registered commands without errors on 4.7.2. v0.8.0 is the first version whose config reaches web exports. `disable_in_release_build` only turns the console off: the scripts and about 9 MB of fonts still ship. Enable the plugin once in the editor and commit `project.godot` and `addons/limbo_console.cfg`. Whether the console stays on in the itch build is still open.
- **gdtoolkit `4.5.0`**: the latest release. It parsed every GDScript syntax form I tried on 4.7.2. Between 4.5 and 4.7.2 the engine's keywords and annotations are unchanged, and the only new parser feature test is multiline `preload(…,)`, which gdtoolkit also parses. The maintainer has been inactive since October 2025. `gdformat` can produce files Godot rejects (#424, reproduced) and duplicates comments, so hooks should use `gdlint` and `gdformat --check`. Hooks must also filter out `addons/` themselves (#395) and must not run in parallel (#428).
- **CI Godot**: `chickensoft-games/setup-godot@v2.4.3` with `version: 4.7.2`, `use-dotnet: false` (it defaults to true) and `include-templates: true`. Then run `--import` followed by `--export-release "Web" build/web/index.html`. godot-ci's `4.7.2` image works but is 2.6 GB.
- **Deploy**: run the butler CLI pinned to `15.32.0` from broth, not the butler action, which always fetches butler `LATEST`. The only secret is `BUTLER_API_KEY`, plus a non-secret variable `ITCH_TARGET=user/game` and channel `html5`. HTML5 is never auto-tagged: after the first push, mark the channel "Playable in browser" by hand (ticket 08).

[findings](../research/03-plugins-and-ci-compat.md)
