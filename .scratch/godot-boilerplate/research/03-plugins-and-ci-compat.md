# Plugins and CI compatibility with Godot 4.7.2

Research for [issue 03](../issues/03-plugins-and-ci-compat.md). Checked on 2026-10-07 against primary sources (the GitHub repos, PyPI, itch.io butler docs and docs.godotengine.org), plus local runs with **Godot v4.7.2.stable.official.ed1daf0bf** (macOS arm64).

Godot 4.7.2-stable was released 2026-08-18 ([godotengine/godot releases](https://github.com/godotengine/godot/releases/tag/4.7.2-stable)).

Legend: **[verified]** means I checked it locally on 4.7.2. **[source]** means a primary source states it. **[unverified]** means no source covers it and I did not test it.

---

## 1. gdUnit4 (tests)

**Pin: gdUnit4 `v6.2.1`** (tag commit `08ffc7c65b61b1b2edd545616061a99973c13ce1`, released 2026-08-20). [Release v6.2.1](https://github.com/godot-gdunit-labs/gdUnit4/releases/tag/v6.2.1)

### Compatibility
- The README's compatibility table lists `v6.2.0`: "v4.5 … v4.7, v4.7.1" and `master (v6.2.1)`: the same list plus `v4.8.dev7`. **4.7.2 is not listed by name**, because the table and badges stop at 4.7.1. [source: README "Compatibility Overview"](https://github.com/godot-gdunit-labs/gdUnit4#compatibility-overview)
- The repo's own PR CI matrix runs `['4.5' … '4.7', '4.7.1']` stable plus `4.8-dev7`. 4.7.2 is not in it. [source: ci-pr.yml](https://github.com/godot-gdunit-labs/gdUnit4/blob/master/.github/workflows/ci-pr.yml)
- A user filed issue [#1323](https://github.com/godot-gdunit-labs/gdUnit4/issues/1323) against gdUnit4 6.2.0 on Godot `4.7.2.stable`. The bug was a `runtest.sh` shebang problem on NixOS, not an engine incompatibility, and it is closed.
- **[verified]** I vendored v6.2.1 (without `addons/gdUnit4/test/`) into a scratch project with LimboConsole v0.8.0. I re-ran it in a clean project that held only these two addons and the test. Import: exit 0, and the only lines matching "error" were class names. Tests: exit 0, 2/2 passed, no script or parse errors. `godot --headless --import` printed zero errors or warnings. A two-test suite passed: exit `0`, with `reports/report_1/results.xml` and `index.html` written. A deliberately failing test exited `100`.
- v6.x needs Godot ≥ 4.5. v5.x is for 4.3–4.4. [source: README table](https://github.com/godot-gdunit-labs/gdUnit4#compatibility-overview)

### Install (vendored)
- There are **no release zip assets**. Releases are source tags only ([release page](https://github.com/godot-gdunit-labs/gdUnit4/releases/tag/v6.2.1)). Copy `addons/gdUnit4/` out of the tag archive `https://github.com/godot-gdunit-labs/gdUnit4/archive/refs/tags/v6.2.1.tar.gz`. The official installer ([install doc](https://github.com/godot-gdunit-labs/gdUnit4/blob/v6.2.1/documentation/doc/_first_steps/install.md)) says to put it under `addons/`, enable it in Project Settings → Plugins, and restart the editor.
- Leave out `addons/gdUnit4/test/`, which is gdUnit4's self-test suite. The official action deletes it too unless it is self-testing ([action.yml](https://github.com/godot-gdunit-labs/gdUnit4-action/blob/v1.3.2/action.yml)). Vendored size without it: about 1.7 MB **[verified]**.
- The plugin version is read from `addons/gdUnit4/plugin.cfg`. The action's `version: installed` mode relies on this ([versioning/action.yml](https://github.com/godot-gdunit-labs/gdUnit4-action/blob/v1.3.2/.gdunit4_action/versioning/action.yml)).

### Headless CLI
- Tool: `res://addons/gdUnit4/bin/GdUnitCmdTool.gd`, wrapped by `addons/gdUnit4/runtest.sh` (and `runtest.cmd` on Windows). It needs `GODOT_BIN` or `--godot_binary <path>`. [source: cmd docs](https://github.com/godot-gdunit-labs/gdUnit4/blob/v6.2.1/documentation/doc/_advanced_testing/cmd.md), [runtest.sh](https://github.com/godot-gdunit-labs/gdUnit4/blob/v6.2.1/addons/gdUnit4/runtest.sh)
- Main options: `-a <dir|suite>` adds tests, `-i <suite|suite:test>` ignores them, `-c` continues after the first failure (the default is fail-fast), `-conf [cfg]` re-runs the last inspector run, `-rd <dir>` sets the report dir (default `res://reports/`) and `-rc <n>` keeps n reports (default 20). [source: cmd docs](https://github.com/godot-gdunit-labs/gdUnit4/blob/v6.2.1/documentation/doc/_advanced_testing/cmd.md)
- Return codes: `0` all passed, `100` failures, `101` warnings. [source: cmd docs "Return Codes"](https://github.com/godot-gdunit-labs/gdUnit4/blob/v6.2.1/documentation/doc/_advanced_testing/cmd.md). I also saw `103`, an abnormal exit, when headless mode was refused (see the next bullet) **[verified]**.
- **Caveat: headless mode is refused by default.** Under `--headless`, the runner prints "Headless mode is not supported! … Godot 'InputEvents' are not transported by the Godot engine in headless mode" and exits `103` unless you pass `--ignoreHeadlessMode`. [source: GdUnitTestCIRunner.gd](https://github.com/godot-gdunit-labs/gdUnit4/blob/v6.2.1/addons/gdUnit4/src/core/runners/GdUnitTestCIRunner.gd) **[verified]**. Local agent command:
  `GODOT_BIN=/path/to/godot ./addons/gdUnit4/runtest.sh --headless -a res://test --ignoreHeadlessMode`
- `runtest.sh` passes `--remote-debug tcp://127.0.0.1:0` so that a parse error cannot drop Godot into an interactive `debug>` loop, which matters for agents. [source: runtest.sh](https://github.com/godot-gdunit-labs/gdUnit4/blob/v6.2.1/addons/gdUnit4/runtest.sh)

### Report formats
- HTML (`index.html`) and JUnit XML (`results.xml`) under `reports/report_N/`. [source: cmd docs "The Report"](https://github.com/godot-gdunit-labs/gdUnit4/blob/v6.2.1/documentation/doc/_advanced_testing/cmd.md) **[verified]**. The docs say `index.htm`, but v6.2.1 actually writes `index.html`. Add `reports/` to `.gitignore`.

### Official GitHub Action
- **Pin `godot-gdunit-labs/gdUnit4-action@v1.3.2`** (commit `17eeffa988f9732fdc3dba3067405d16b55809de`, released 2026-06-28). [releases](https://github.com/godot-gdunit-labs/gdUnit4-action/releases). The README itself says "Use specific versions instead of 'latest'". [README](https://github.com/godot-gdunit-labs/gdUnit4-action#best-practices)
- Inputs we need: `godot-version: '4.7.2'`, `version: installed` (use the vendored addon, no clone), `paths: res://test`, `timeout`, `report-name`, `warnings-as-errors`, `publish-report`. [README Configuration](https://github.com/godot-gdunit-labs/gdUnit4-action#configuration), [action.yml](https://github.com/godot-gdunit-labs/gdUnit4-action/blob/v1.3.2/action.yml)
- How it works:
  - It downloads Godot itself from `github.com/godotengine/godot-builds/releases/download/<ver>-<status>` and caches it with `actions/cache` ([godot-install](https://github.com/godot-gdunit-labs/gdUnit4-action/blob/v1.3.2/.gdunit4_action/godot-install/action.yml)). The test job needs no separate Godot setup step.
  - It restores the project cache with `godot --path ./ -e --headless --quit-after 2000`, then runs `xvfb-run --auto-servernum ./addons/gdUnit4/runtest.sh --audio-driver Dummy --display-driver x11 --rendering-driver opengl3 --single-window --continue --add <paths>`. So in CI it runs **under a virtual X display with OpenGL3, not headless**, and input-event tests work there. [action.yml](https://github.com/godot-gdunit-labs/gdUnit4-action/blob/v1.3.2/action.yml), [unit-test/index.js](https://github.com/godot-gdunit-labs/gdUnit4-action/blob/v1.3.2/.gdunit4_action/unit-test/index.js)
  - It publishes the JUnit report with `dorny/test-reporter@v3` and uploads report artifacts. [publish-test-report](https://github.com/godot-gdunit-labs/gdUnit4-action/blob/v1.3.2/.gdunit4_action/publish-test-report/action.yml)
  - Its compatibility gate maps gdUnit4 `6.0.0`+ to Godot `4.5`–`5.0`, so `4.7.2` + `6.2.1` passes. [compatibility_matrix.json](https://github.com/godot-gdunit-labs/gdUnit4-action/blob/v1.3.2/.gdunit4_action/versioning/check/compatibility_matrix.json)
- Permissions: gdUnit4's own example job grants `actions/checks/contents/pull-requests/statuses: write`. For fork PRs, set `publish-report: false`. [ci.md FAQ](https://github.com/godot-gdunit-labs/gdUnit4/blob/v6.2.1/documentation/doc/_faq/ci.md), [README Security](https://github.com/godot-gdunit-labs/gdUnit4-action#security)

### Caveats
- No source names 4.7.2. Evidence for it: the 4.7.1 matrix, the action's 4.5–5.0 gate, a user running 6.2.0 on 4.7.2 (#1323), and my local run. **[unverified]** gdUnit4 under xvfb on the Linux runner with 4.7.2 specifically; it should match 4.7.1, which upstream CI covers.
- **[unverified]** UI/input-event tests in headless runs. Upstream says they don't work, which is why CI uses xvfb.
- gdUnit4 is an editor plugin. Keep `addons/gdUnit4/*` and `test/*` out of the web export with the Web preset's `exclude_filter`. This is my recommendation; gdUnit4's docs don't cover it.

---

## 2. LimboConsole (dev console)

**Pin: LimboConsole `v0.8.0`** (tag commit `969f5d461efa4eb7a1689ede6572db8e1b1fa70d`, released 2026-06-20, two days after 4.7-stable). Release asset: `limbo_console_v0.8.0.zip`, already laid out as `addons/limbo_console/`. [Release v0.8.0](https://github.com/limbonaut/limbo_console/releases/tag/v0.8.0)

### Compatibility
- **No stated 4.7 support anywhere.** The README badge still says "Godot-4.3" ([README](https://github.com/limbonaut/limbo_console)), and the release notes say nothing about engine versions. The README warns: "This plugin is currently in development, so expect breaking changes."
- **[verified]** On 4.7.2: headless import of v0.8.0 with its autoload registered gave zero errors. From a gdUnit4 test, `LimboConsole.register_command(...)`, `has_command(...)` and `unregister_command(...)` all worked.
- Closed issue [#84](https://github.com/limbonaut/limbo_console/issues/84) ("Type safe errors in Godot 4.6") was a duplicate-install mistake, not a 4.6 incompatibility. Open issue [#72](https://github.com/limbonaut/limbo_console/issues/72) ("Identifier 'LimboConsole' not declared") appears when the autoload isn't registered.
- Unreleased commits on `master` after 0.8.0: `override_command` ([#93](https://github.com/limbonaut/limbo_console/pull/93)) and "skip errors when unregistering" ([#92](https://github.com/limbonaut/limbo_console/pull/92)). Neither is needed, so stay on the tag.

### Install (vendored)
- Put the code at `res://addons/limbo_console/` and enable the plugin. The default toggle key is backtick. [README "How to use"](https://github.com/limbonaut/limbo_console#how-to-use)
- **Caveat for vendoring:** the plugin's `_enable_plugin()` adds the `LimboConsole` autoload and the input actions `limbo_console_toggle`, `limbo_auto_complete_reverse` and `limbo_console_search_history`, and creates `res://addons/limbo_console.cfg`. That only happens when the plugin is toggled on in the editor ([plugin.gd](https://github.com/limbonaut/limbo_console/blob/v0.8.0/plugin.gd)). **[verified]** Just listing it under `[editor_plugins]` in `project.godot` and importing headlessly did **not** create the cfg. Enable it once in the editor and commit `project.godot` and `addons/limbo_console.cfg`.
- **Web size:** the addon ships five Monaspace Argon OTF fonts, 8.9 MB of the 9.0 MB addon **[verified, source size]**. **[unverified]** How much this adds to the exported web `.pck`. For a web-first jam, consider pointing the theme at one small font.

### Registering commands
```gdscript
func _ready() -> void:
    LimboConsole.register_command(multiply, "math multiply", "Multiply two numbers")
    LimboConsole.add_argument_autocomplete_source("teleport", 0, func(): return ["entrance", "caves"])
```
Argument types are bool, int, float, String, StringName and Vector2/3/4. Subcommands use a space in the name. There is also `unregister_command`, `add_alias`, `info/warning/error`, `execute_script` (`.lcs` scripts, `user://autoexec.lcs`). [README](https://github.com/limbonaut/limbo_console#how-to-use), [v0.8.0 notes (StringName args, on/off booleans)](https://github.com/limbonaut/limbo_console/releases/tag/v0.8.0)

### Release / web builds
- Config `disable_in_release_build` (default `false`): when `true`, `enabled = OS.is_debug_build()`. Separately, `commands_disabled_in_release` (default `["eval"]`) blocks listed commands in non-debug builds. [console_options.gd](https://github.com/limbonaut/limbo_console/blob/v0.8.0/console_options.gd), [limbo_console.gd](https://github.com/limbonaut/limbo_console/blob/v0.8.0/limbo_console.gd)
- **This disables the console; it does not strip it.** The autoload, scripts and fonts still ship in the export. Stripping it would mean removing the autoload and excluding the folder, and then every `LimboConsole.*` call in game code would fail to parse. That is why game code should only register commands from a few dev-only places.
- Bug fixed in v0.8.0: the cfg file was missing from web exports, so `disable_in_release_build` was ignored on web ([#87](https://github.com/limbonaut/limbo_console/issues/87)). It was fixed by "Auto-include console config on project export" ([#89](https://github.com/limbonaut/limbo_console/pull/89), [export_plugin.gd](https://github.com/limbonaut/limbo_console/blob/v0.8.0/export_plugin.gd)). **Do not use versions before 0.8.0.**
- **Decision for the parent (not decided here):** the itch build is an `--export-release`, so `OS.is_debug_build()` is false there. Either set `disable_in_release_build=true` (no console on itch) or leave it `false` (console usable on itch for playtesting, with `eval` still blocked).

---

## 3. gdtoolkit (`gdlint` / `gdformat`)

**Pin: `gdtoolkit==4.5.0`** (PyPI, uploaded 2025-10-09, `requires_python >=3.7`). It is the latest release. [PyPI](https://pypi.org/project/gdtoolkit/), [GitHub release 4.5.0](https://github.com/Scony/godot-gdscript-toolkit/releases/tag/4.5.0)

### Syntax coverage for 4.5–4.7
- 4.5.0 changelog: "Added support for @abstract functions", "Added support for variadic functions", plus `@warning_ignore_start/restore` formatting fixes. Typed dictionaries arrived in 4.3.2, `is not` in 4.3.1, and guarded `match` (`when`) in 4.3.0. [CHANGELOG](https://github.com/Scony/godot-gdscript-toolkit/blob/master/CHANGELOG.md)
- **What changed in GDScript syntax between 4.5 and 4.7.2:** I compared the engine sources at tags `4.5-stable` and `4.7.2-stable`. The keyword table in `gdscript_tokenizer.cpp` and the `register_annotation` list in `gdscript_parser.cpp` are identical apart from whitespace. The only new parser feature test is `multiline_preload.gd`, which covers `preload(` across lines with a trailing comma. [features @4.7.2](https://github.com/godotengine/godot/tree/4.7.2-stable/modules/gdscript/tests/scripts/parser/features). The 4.7 migration guide lists only API renames and behaviour changes, such as "Methods that inherit from a method with a typed return now inherit the return type as well". [upgrading_to_godot_4.7](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.7.html)
- **[verified]** I wrote a file containing `@abstract class_name`, `@abstract func`, a variadic `...values: Array`, `Dictionary[Vector2i, StringName]`, a property `set/get`, `match` with `when`, `is not`, a multi-statement lambda, `await`, `@warning_ignore_start/restore`, `static func`, and a multiline `preload(…,)`. Godot 4.7.2 `--check-only` accepted it. `gdlint` 4.5.0 reported no problems. `gdformat` reformatted it (`@abstract` joined onto the `class_name` line, blank lines added around `@warning_ignore_*`) and **the result still parsed in 4.7.2**.

### Install / invocation
- `uvx --from gdtoolkit==4.5.0 gdlint <paths>`, `uvx --from gdtoolkit==4.5.0 gdformat --check <paths>`. pip or pipx work the same way. [README](https://github.com/Scony/godot-gdscript-toolkit)
- gdUnit4's own CI uses `Scony/godot-gdscript-toolkit@master` with `version: 4.5.0` ([gdlint.yml](https://github.com/godot-gdunit-labs/gdUnit4/blob/master/.github/workflows/gdlint.yml)). Pinning the PyPI version through `uvx`/pip is more explicit than an `@master` action ref.

### Config format
- `gdlint` reads a YAML `gdlintrc` (or `.gdlintrc`). `gdlint --dump-default-config` writes the defaults. Notable keys: `excluded_directories` (a YAML `!!set`, default `.git`), `disable: []`, the naming regexes, `max-line-length: 100`, `max-file-lines: 1000`, `function-arguments-number: 10`, `max-returns: 6`, `max-public-methods: 20`, `class-definitions-order`. **[verified]** with the dump.
- `gdformat` reads `gdformatrc` (added in 4.3.0, [CHANGELOG](https://github.com/Scony/godot-gdscript-toolkit/blob/master/CHANGELOG.md)). Options include line length and spaces-vs-tabs ([#352](https://github.com/Scony/godot-gdscript-toolkit/pull/352)).
- `gdlint --dump-default-config` crashes with `AssertionError` if a `gdlintrc` already exists in the current directory. [#426](https://github.com/Scony/godot-gdscript-toolkit/issues/426)

### Caveats and known false positives
- **The maintainer looks inactive.** The last commit on `master` was 2025-10-09, and there have been about a dozen bug reports since with no response. [commits](https://github.com/Scony/godot-gdscript-toolkit/commits/master), [issues](https://github.com/Scony/godot-gdscript-toolkit/issues)
- **`gdformat` can produce code Godot rejects.** A multiline lambda as the last argument of a nested call gets staircase closers, and the result fails with `Parse Error: Unindent doesn't match the previous indentation level.` [#424](https://github.com/Scony/godot-gdscript-toolkit/issues/424). **[verified]** I reproduced it on 4.5.0 with 4.7.2: the input parsed, the formatted output failed.
- **`gdformat` duplicates comments** into split collection literals and lambda bodies. [#432](https://github.com/Scony/godot-gdscript-toolkit/issues/432), [#417](https://github.com/Scony/godot-gdscript-toolkit/issues/417)
- **`excluded_directories` is ignored when files are passed explicitly** (e.g. `gdlint addons/foo.gd`), which is how pre-commit and Claude hooks call it. [#395](https://github.com/Scony/godot-gdscript-toolkit/issues/395). The hook itself must filter out `addons/`. **[verified]** how noisy vendored code is: `gdlint addons/gdUnit4` gives 1101 problems, `addons/limbo_console` gives 46, and `gdformat --check addons/` would reformat 222 files.
- **Running two instances at once can fail spuriously** with `Cannot open file '<x>.gd': File exists` because of a race on the grammar cache directory. [#428](https://github.com/Scony/godot-gdscript-toolkit/issues/428). This matters if the Claude Code hook and the git pre-commit hook overlap. Run gdlint once to warm the cache, or don't run the two in parallel.
- `@abstract func f();` with a trailing semicolon fails to parse in gdlint. [#430](https://github.com/Scony/godot-gdscript-toolkit/issues/430)
- `static func` is missing from the AST, so `function-arguments-number`, `max-returns` and `max-public-methods` never check static functions. [#425](https://github.com/Scony/godot-gdscript-toolkit/issues/425)
- `function-preload-variable-name` demands PascalCase even for preloaded scenes. [#418](https://github.com/Scony/godot-gdscript-toolkit/issues/418)
- `gdformat` and `gdlint` disagree by one on line length for `@abstract func`. [#419](https://github.com/Scony/godot-gdscript-toolkit/issues/419)
- Use `gdformat --check` in hooks. If agents may auto-format, follow it with a Godot parse check of the changed files, and grep the output for `SCRIPT ERROR`/`Parse Error` (see the next note).
- Side finding **[verified]**: on 4.7.2, `godot --headless --check-only -s res://bad.gd` printed `SCRIPT ERROR: Parse Error …` but still **exited 0**. A parse check has to inspect stderr; the exit code alone tells you nothing. (This belongs with ticket 02's headless research.)

---

## 4. Installing Godot 4.7.2 + export templates in CI

Binaries: `Godot_v4.7.2-stable_linux.x86_64.zip` (78 MB) and `Godot_v4.7.2-stable_export_templates.tpz` (**1.28 GB**, all platforms in one archive) on [godot-builds 4.7.2-stable](https://github.com/godotengine/godot-builds/releases/tag/4.7.2-stable).

| Option | Version | Notes |
|---|---|---|
| **chickensoft-games/setup-godot** (recommended for export) | `v2.4.3` (2026-10-01, commit `ac93246ea68518a384c1c280a496e5989341f2f6`) [releases](https://github.com/chickensoft-games/setup-godot/releases) | Downloads from godot-builds, caches it, puts `godot` on PATH and sets `GODOT`/`GODOT4`. With `include-templates: true` it installs templates to `~/.local/share/godot/export_templates/<ver>`. **`use-dotnet` defaults to `true`, so set it to `false`.** `version` needs major.minor.patch (`4.7.2`). [README](https://github.com/chickensoft-games/setup-godot), [action.yml](https://github.com/chickensoft-games/setup-godot/blob/v2.4.3/action.yml), [src](https://github.com/chickensoft-games/setup-godot/blob/v2.4.3/src/main.ts) |
| gdUnit4-action's built-in install | `v1.3.2` | Covers the test job only (no templates). See §1. |
| abarichello/godot-ci (Docker) | image tag `barichello/godot-ci:4.7.2` (GitHub release `4.7.2-stable`, 2026-08-18) [releases](https://github.com/abarichello/godot-ci/releases), [Docker Hub](https://hub.docker.com/r/barichello/godot-ci/) | Godot, templates and butler in one container. But the image is about **2.6 GB** compressed because it bundles the Android SDK, NDK and JDK ([Dockerfile](https://github.com/abarichello/godot-ci/blob/master/Dockerfile)). Butler comes from `getbutler.sh` at image build time, so it isn't pinned by us. Its example workflow has to `mv` the templates from `/root` ([godot-ci.yml](https://github.com/abarichello/godot-ci/blob/master/.github/workflows/godot-ci.yml)). Not recommended. |
| Raw download | n/a | `wget` both files, `unzip` the binary, and extract `templates/*` into `~/.local/share/godot/export_templates/4.7.2.stable/`. This is exactly what godot-ci's Dockerfile does. It's fine, but it reimplements caching. |

### Headless web export
- `godot --headless --path . --export-release "Web" build/web/index.html`. The preset name must match one in `export_presets.cfg`, which has to be committed. A relative output path is relative to the directory that contains `project.godot`. `--headless` is required on runners without a GPU. [command line tutorial (4.7)](https://docs.godotengine.org/en/4.7/tutorials/editor/command_line_tutorial.html), [godot-ci troubleshooting](https://github.com/abarichello/godot-ci#problems-while-exporting)
- In the 4.7.2 source, every `--export-*` flag sets `wait_for_import = true` ([main.cpp](https://github.com/godotengine/godot/blob/4.7.2-stable/main/main.cpp)). The docs only spell out "Implies `--import`" for `--export-debug` and `--export-pack`. An explicit `godot --headless --path . --import` step on a fresh checkout is cheap insurance.
- Web-specific settings (threads, SharedArrayBuffer, renderer) belong to ticket 01.

---

## 5. Deploying to itch.io with butler

**Pin: butler `15.32.0`** (latest, 2026-10-06). [itchio/butler releases](https://github.com/itchio/butler/releases). Broth reports `LATEST` = `15.32.0`, and a version-pinned URL works:
`https://broth.itch.zone/butler/linux-amd64/15.32.0/archive/default` (it redirects to the archive; **[verified]** with curl).

- **Install (non-interactive):** the docs give `https://broth.itch.zone/butler/linux-amd64/LATEST/archive/default`, then `unzip`, `chmod +x` and add it to PATH. The zip also contains two 7-zip libraries. [installing](https://itch.io/docs/butler/installing.html). Replace `LATEST` with the version to pin.
- **Auth in CI:** set the `BUTLER_API_KEY` env var. Get the key from https://itch.io/user/settings/api-keys (the `wharf` entry) or from `butler_creds` after a local `butler login`. "if your API key appears in a public build log, consider it burned and revoke it immediately". [login](https://itch.io/docs/butler/login.html)
- **Push:** `butler push <dir> user/game:channel`. Optional flags: `--userversion <v>` or `--userversion-file`, `--if-changed` (skip the push when nothing changed), `--dry-run`, `--ignore <glob>`. [pushing](https://itch.io/docs/butler/pushing.html)
- **Channel naming:** use kebab-case. Names containing `win`/`windows`, `linux`, `mac`/`osx` or `android` get the matching platform tag automatically. **No channel name is auto-tagged as HTML5.** "Tagging a channel as 'HTML5 / Playable in browser' needs to be done from the itch.io Edit game page, once the first build is pushed". The project kind must also be set to HTML. [pushing](https://itch.io/docs/butler/pushing.html). I suggest the channel `html5`. Ticket 08 needs this manual step: push once, then tick "This file will be played in the browser".
- **Action option:** `manleydev/butler-publish-itchio-action` now redirects to `yeslayla/butler-publish-itchio-action`, latest `v1.2.0` (2026-03-08). It is a Docker action whose Dockerfile curls butler **`LATEST`** on every run, then `butler push "$PACKAGE" $ITCH_USER/$ITCH_GAME:$CHANNEL [--userversion]`, taking env `BUTLER_CREDENTIALS`, `CHANNEL`, `ITCH_GAME`, `ITCH_USER`, `PACKAGE`, `VERSION`/`VERSION_FILE`. [README](https://github.com/yeslayla/butler-publish-itchio-action), [Dockerfile](https://github.com/yeslayla/butler-publish-itchio-action/blob/v1.2.0/Dockerfile), [entrypoint.sh](https://github.com/yeslayla/butler-publish-itchio-action/blob/v1.2.0/entrypoint.sh). The butler version can't be pinned and there's no `--if-changed`, and the wrapper is only a few lines, so **calling the butler CLI directly is simpler and pinned**.

---

## Implications for the boilerplate

### Exact versions to pin
| Thing | Pin | Where |
|---|---|---|
| Godot | `4.7.2` (stable) | CI inputs, team installs |
| gdUnit4 | `v6.2.1` (`addons/gdUnit4/`, without `test/`) | vendored |
| LimboConsole | `v0.8.0` (`addons/limbo_console/`) + committed `addons/limbo_console.cfg` | vendored |
| gdtoolkit | `4.5.0` | `uvx --from gdtoolkit==4.5.0` in hooks/CI |
| gdUnit4-action | `v1.3.2` (or SHA `17eeffa988f9732fdc3dba3067405d16b55809de`) | PR workflow |
| setup-godot | `v2.4.3` (or SHA `ac93246ea68518a384c1c280a496e5989341f2f6`) | deploy workflow |
| actions/checkout | `v7.0.1` | both |
| butler | `15.32.0` via broth URL | deploy workflow |

Version check for actions/checkout on 2026-10-07: latest release `v7.0.1` ([releases](https://github.com/actions/checkout/releases)).

### Recommended Actions
- PR tests: `godot-gdunit-labs/gdUnit4-action@v1.3.2` with `version: installed`. It runs under xvfb in CI, so no `--ignoreHeadlessMode` is needed there.
- Deploy: `chickensoft-games/setup-godot@v2.4.3` (`use-dotnet: false`, `include-templates: true`) plus the butler CLI from broth. Not godot-ci (2.6 GB image) and not the butler action (unpinned `LATEST`).

### GitHub secrets and variables
- **Secret:** `BUTLER_API_KEY`, the only secret.
- **Variable (not secret):** `ITCH_TARGET` = `user/game`, for example. The channel `html5` can be hard-coded.
- Ticket 08 records the real values and does the one-time "Playable in browser" tick after the first push.

### Repo hygiene implied
- Commit `export_presets.cfg` with a preset named exactly `Web`. In it, set `exclude_filter` for `addons/gdUnit4/*, test/*`.
- `.gitignore`: `reports/`, `build/`, `.godot/`.
- The lint hooks must skip `addons/` themselves (gdtoolkit #395), must not run in parallel with each other (#428), and should use `gdformat --check`, not auto-write, unless followed by a Godot parse check (#424).

### Sketch: PR tests (`.github/workflows/pr-tests.yml`)
```yaml
name: pr-tests
on:
  pull_request:
concurrency:
  group: pr-tests-${{ github.event.number }}
  cancel-in-progress: true
jobs:
  test:
    runs-on: ubuntu-24.04
    timeout-minutes: 15
    permissions:
      actions: write
      checks: write
      contents: write
      pull-requests: write
      statuses: write
    steps:
      - uses: actions/checkout@v7.0.1
      - uses: godot-gdunit-labs/gdUnit4-action@v1.3.2
        with:
          godot-version: '4.7.2'
          version: installed          # use vendored addons/gdUnit4 (reads plugin.cfg)
          paths: res://test
          timeout: 10
          warnings-as-errors: false
          report-name: test-report.xml
```
Make the `test` job a required status check on `main`. A `gdlint` job (`uvx --from gdtoolkit==4.5.0 gdlint <non-addon dirs>`) would be a cheap backstop if people bypass the local hooks, but the map puts linting local-only.

### Sketch: main → itch.io (`.github/workflows/deploy-web.yml`)
```yaml
name: deploy-web
on:
  push:
    branches: [main]
concurrency:
  group: deploy-web
  cancel-in-progress: true
jobs:
  deploy:
    runs-on: ubuntu-24.04
    timeout-minutes: 20
    steps:
      - uses: actions/checkout@v7.0.1
      - uses: chickensoft-games/setup-godot@v2.4.3
        with:
          version: 4.7.2
          use-dotnet: false
          include-templates: true
      - name: Import project
        run: godot --headless --path . --import
      - name: Export web
        run: |
          mkdir -p build/web
          godot --headless --path . --export-release "Web" build/web/index.html
          test -f build/web/index.html
      - name: Install butler 15.32.0
        run: |
          curl -fsSL -o "$RUNNER_TEMP/butler.zip" https://broth.itch.zone/butler/linux-amd64/15.32.0/archive/default
          unzip -q "$RUNNER_TEMP/butler.zip" -d "$RUNNER_TEMP/butler"
          chmod +x "$RUNNER_TEMP/butler/butler"
          echo "$RUNNER_TEMP/butler" >> "$GITHUB_PATH"
      - name: Push to itch.io
        env:
          BUTLER_API_KEY: ${{ secrets.BUTLER_API_KEY }}
        run: |
          butler push build/web "${{ vars.ITCH_TARGET }}:html5" \
            --userversion "${{ github.run_number }}-${GITHUB_SHA::7}" --if-changed
```
Merges are squashes of PRs that already passed `pr-tests`, so the deploy job doesn't rerun the tests.

### Still unverified
- gdUnit4 and LimboConsole **by name** against 4.7.2. Upstream stops at 4.7.1 or says nothing; my local 4.7.2 import and test run passed.
- Both workflow sketches are untested on a real runner, including setup-godot downloading and caching the 1.28 GB template archive, and xvfb + OpenGL3 on `ubuntu-24.04` with 4.7.2.
- LimboConsole inside an actual web export (cfg pickup, size added by the fonts).
- UI/input-event gdUnit4 tests under xvfb in CI.
