# Research: headless Godot 4.7.2 for agents, and the Godot MCP landscape

Ticket: [02-headless-godot-and-mcp](../issues/02-headless-godot-and-mcp.md) · Researched 2026-10-07

**Evidence labels**
- **[RUN-mac]**: I ran it with `/opt/homebrew/bin/godot` (4.7.2.stable.official.ed1daf0bf, macOS arm64) in a throwaway project in the session scratchpad.
- **[RUN-linux]**: I ran it with the official `Godot_v4.7.2-stable_linux.arm64` binary in an `ubuntu:24.04` Docker container.
- **[SRC]**: I read it in Godot's or the plugin's source at the release tag.
- **[DOCS]**: from docs.godotengine.org (4.7) or the plugin's own docs.
- **[API]**: data I pulled from the GitHub API.
- **[README]**: a claim in a project's README that I did not test.

---

## 1. What the 4.7.2 CLI can do headlessly

`godot --help` on 4.7.2 shows the relevant flags [RUN-mac]:
- `--headless` is shorthand for `--display-driver headless --audio-driver Dummy`.
- Run flags: `--quit`, `--quit-after <int>`, `--path`, `--scene <path|uid>`, `--log-file <file>`, `--write-movie <file>`.
- Tool flags: `-s/--script`, `--check-only`, `--import`, `--export-release|--export-debug|--export-pack <preset> <path>`.
- Editor-only flags (help legend "E"): `--lsp-port` and `--dap-port`.

There is no built-in lint or test runner flag.

### 1.1 Script checking: `--check-only -s`

```sh
godot --headless --path <proj> --check-only -s res://path/to/script.gd
```

**What it catches** [RUN-mac]:
- Syntax errors.
- Static type errors.
- Calls to undefined functions.
- Missing `preload` targets.
- Undeclared identifiers.

Each error prints to stderr as `SCRIPT ERROR: Parse Error: … at: GDScript::reload (res://file.gd:<line>)`. It costs about 0.15 s per file.

**Gotchas, each verified:**

1. **The exit code is wrong on macOS and right on Linux.**
   - A script with parse errors exits **0** on macOS [RUN-mac] and **1** on Linux [RUN-linux], using the same project and the same scripts.
   - The cause is in the source [SRC]:
     - `main/main.cpp` returns `script_res->is_valid() ? EXIT_SUCCESS : EXIT_FAILURE`.
     - `platform/linuxbsd/godot_linuxbsd.cpp` calls `os.set_exit_code(EXIT_FAILURE)` when `Main::start()` fails.
     - `OS_MacOS_Headless::run()` in `platform/macos/os_macos.mm` never sets the exit code when that happens.
   - **What to do:** locally on macOS, detect failures by grepping stderr for `SCRIPT ERROR`. In Linux CI, the exit code can be trusted.

2. **Global `class_name` classes need an import first.**
   - On a fresh clone with no `.godot/`, a script that uses another script's `class_name` fails with `Identifier "Foo" not declared in the current scope`.
   - After `godot --headless --path <proj> --import`, which writes `.godot/global_script_class_cache.cfg`, the `Foo` error disappears [RUN-mac]. The test script then failed only on its autoload reference, which is gotcha 3.

3. **Autoload singletons are false positives, even after import.**
   - A script that references an autoload, for example `Events.ping.emit()`, fails with `Compile Error: Identifier not found: Events` [RUN-mac].
   - This is open upstream as godotengine/godot#78587 (open since 4.0) and #111515.
   - It matters a lot here, because the planned signal bus is an autoload.

4. **Warnings are not reported.** An unused local variable produces no output [RUN-mac].

5. **Never add `-d`/`--debug` to a check run.**
   - On a script error, the local stdout debugger waits for input (`debug>`) and hangs. This is godotengine/godot#117123.
   - gdUnit4's `runtest.sh` passes `--remote-debug tcp://127.0.0.1:0` specifically to avoid this [SRC].

**A better whole-project check, verified [RUN-mac].** Use a `SceneTree` script that `load()`s every `.gd` file and exits non-zero on any failure:
- Because it runs as a real MainLoop, autoloads exist, so gotcha 3 does not occur.
- The exit code comes from `quit(n)`, which works on macOS (a `quit(3)` test exited with code 3), so gotcha 1 does not occur either. I did not run the checker on Linux.

The core of the script (about 20 lines):

```gdscript
extends SceneTree
func _initialize() -> void:
	var me: String = get_script().resource_path
	var failed := 0
	for path in _scripts("res://"):          # recursive walk, skips dot-dirs and addons/
		if path == me: continue              # loading itself with CACHE_MODE_IGNORE hung the run
		var s: Script = ResourceLoader.load(path, "", ResourceLoader.CACHE_MODE_IGNORE)
		if s == null or not s.can_instantiate():
			failed += 1
			printerr("FAILED: ", path)
	quit(1 if failed > 0 else 0)
```

The test project contained a broken script, a script with type errors, and a script that uses an autoload:
- Output: `FAILED: res://bad.gd`, `FAILED: res://typeerr.gd`, `checked, failures: 2`.
- Exit code 1.
- The autoload user was correctly *not* flagged.

The first version of this script did not skip itself and hung with no output. Piping Godot through `sed | grep | tail` also hid output, so use `--log-file` or redirect to a file.

### 1.2 Import: `--import`

```sh
godot --headless --path <proj> --import
```
- It runs the first filesystem scan, registers global classes, writes `.godot/`, and writes a `*.uid` sidecar next to every `.gd` file [RUN-mac]. It takes about 2 s on a tiny project.
- The docs say it "Starts the editor, waits for any resources to be imported, and then quits" [DOCS].
- **I saw it crash once.** The first `--import` on a fresh project printed `handle_crash: Program crashed with signal 11` at shutdown, after it had already written the class cache. Three fresh reruns were clean, so this is a flaky crash at exit and I did not measure its exit code. Don't let CI depend on the exit code of `--import` alone. Check for the class cache, or just run the next step.
- **Repository hygiene:** gitignore `.godot/` and commit the `*.uid` files.

### 1.3 Running a scene or a script

```sh
godot --headless --path <proj> --quit-after 120                              # main scene, ~120 frames
godot --headless --path <proj> --scene res://x.tscn --quit-after 60 --log-file <abs path>
godot --headless --path <proj> -s res://tools/foo.gd                         # extends SceneTree/MainLoop
```

All of the following are [RUN-mac]:
- `print()` goes to stdout. `push_warning`, `push_error` and runtime script errors go to **stderr** with a GDScript backtrace, and also to `--log-file`.
- **Runtime errors do not change the exit code.** A null method call (`SCRIPT ERROR: Cannot call method 'queue_free' on a null value` plus a backtrace) and a scene with a broken script and a missing sub-scene both exited **0**. To smoke-test, run the scene and grep stderr or the log for `^(SCRIPT )?ERROR`.
- `-s` scripts get autoloads: `root.has_node("Events")` was true. `quit(n)` sets the exit code.
- Synthetic input works headless. `Input.parse_input_event(InputEventMouseButton)` and `root.push_input(InputEventKey)` both reached `_unhandled_input`, headless and windowed.
  - gdUnit4's headless warning says "InputEvents are not transported … in headless mode" [SRC]. My test disagrees for these simple cases.
  - Untested: gdUnit's scene-runner input, 3D physics picking via mouse, and `get_mouse_position()`.

### 1.4 Screenshots and visual capture

- **`--write-movie` crashes headless.** `--headless --write-movie out.png --quit-after 3` crashes with signal 11 (`Parameter "t" is null` in the dummy texture storage) [RUN-mac].
- **It works windowed.** `godot --path <proj> --write-movie <dir>/frame.png --quit-after 3` opens a window briefly and writes `frame00000000.png`… plus a `.wav` [RUN-mac]:
  - It used the Compatibility renderer (OpenGL 4.1 via Metal).
  - The frames were 1152×648, the project viewport size. `--resolution` did not change it.
  - I opened a frame and the scene had rendered correctly.
  - This is the no-MCP way for an agent to look at the game on a dev Mac.
- **Linux CI would need a virtual display** (xvfb plus Mesa software GL) for the same trick. I did not test this.

### 1.5 Web export

```sh
godot --headless --path <proj> --export-release "Web" build/web/index.html   # target dir must exist
```
- **Missing templates:**
  - It fails clearly and **exits 1** on macOS [RUN-mac]: `No export template found at the expected path: …/export_templates/4.7.2.stable/web_nothreads_release.zip`.
  - Templates are looked up per exact version. This machine has only 4.7.1 templates installed.
- **With templates:**
  - On Linux, from a fresh clone with no `--import` first, it exported `index.html/.js/.wasm/.pck` and the worklets, exit 0 [RUN-linux].
  - Caveat: I mounted the **4.7.1** `web_nothreads_*` templates into the 4.7.2 path. That verifies the CLI pipeline, not real 4.7.2 templates, which are in `Godot_v4.7.2-stable_export_templates.tpz`, 1.28 GB [API].
  - The probe project had no imported assets, so keep `--import` before export in CI.

### 1.6 gdUnit4 tests headless (v6.2.1, released 2026-08-20 [API])

```sh
GODOT_BIN=/opt/homebrew/bin/godot bash addons/gdUnit4/runtest.sh --headless -a res://test --ignoreHeadlessMode
```
- **`runtest.sh` invokes** `"$GODOT_BIN" --path . -s -d --remote-debug tcp://127.0.0.1:0 res://addons/gdUnit4/bin/GdUnitCmdTool.gd <args>` [SRC].
- **Without `--ignoreHeadlessMode`** it refuses: "Headless mode is not supported!" and **exit 103** [RUN-mac]. That code is not in the docs' list of 0, 100 and 101.
- **With the flag:**
  - It ran a passing and a failing test.
  - It printed the failure as `Expecting: 5 but was 4 at … calc_test.gd:5` and **exited 100**.
  - It wrote `reports/report_1/results.xml` (JUnit) and `index.html` [RUN-mac].
- **Documented exit codes:** 0 pass, 100 failures, 101 warnings [DOCS].
- The probe project was imported first. 4.7.2 compatibility across the whole plugin set belongs to ticket 03.

### 1.7 A headless editor for LSP and diagnostics

`godot --headless --editor --path <proj> --lsp-port 6123` keeps running with no window. It listens on 127.0.0.1:6123 for the GDScript LSP and on 6006, the default debug-adapter (DAP) port [RUN-mac]. LSP-based tools that assume "the editor must be open" can therefore use a windowless editor. I did not test any MCP server against it.

---

## 2. Gaps without the editor

| Gap | Headless workaround | Still needs a human or the editor? |
|---|---|---|
| Seeing the game (look, lighting, shader) | Windowed `--write-movie` frame capture, read by the agent (§1.4). Mac dev machines only, not CI without xvfb. | Judging the *feel* of the soft look: yes, human. |
| Inspecting the live scene tree of a running game | `print_tree_pretty()` or a debug dump from an `-s` script, a scene, or LimboConsole. There is no CLI attach to a running game. | Interactive poking: editor Remote tree, or an MCP. |
| Driving the game with mouse input | Synthetic `Input.parse_input_event` works headless (§1.3) and gdUnit scene runner tests. Physics picking is untested. | Playtesting: human. |
| Editing `.tscn` safely | Programmatic: `load()` → `instantiate()` → `add_child` → set `owner` → `PackedScene.pack()` → `ResourceSaver.save()` works headless [RUN-mac]. Godot rewrites `ext_resource` ids (`id="1"` → `id="1_omxwj"`) and adds `unique_id=…` to every node on save. Hand-edited text can work, but expect it to be normalised on the next editor save. Never reuse or duplicate `unique_id`s. | Layout, visual composition, anchors and UI tweaking: editor. |
| Script errors in the editor's view (warnings, live diagnostics) | Whole-project load check (§1.1). LSP via a headless editor (§1.7). | — |
| Importing new assets (textures, models, audio) | `--import` | Import settings tuning: editor. |
| Export presets and project settings | Both are text (`export_presets.cfg`, `project.godot`). | Creating them first: editor is easier. |
| Runtime errors | Grep stderr or `--log-file`. Exit code stays 0 (§1.3). | — |

---

## 3. The Godot MCP landscape (as of 2026-10-07)

Godot ships **no** built-in MCP or AI-agent integration. The 4.5, 4.6 and 4.7 release pages don't mention MCP or AI, and the godotengine org has no such repo.

Methods and limits:
- Stars, dates and licenses are **[API]**. Architecture, tool counts and version support are **[README]** unless marked otherwise.
- I installed or ran **none** of these servers.
- I re-checked the API numbers for the top seven on 2026-10-07.

| Server | Stars | Last push / release | Runtime | Editor must be open? | Tools (claimed) | Godot version claim | Claude Code install (per README) | Sees / drives running game? |
|---|---|---|---|---|---|---|---|---|
| [Coding-Solo/godot-mcp](https://github.com/Coding-Solo/godot-mcp) | 5960 | 2026-04-16, no releases | Node (npx) | **No**: spawns Godot CLI headless | 14 [SRC]: run_project, get_debug_output, create_scene, add_node, save_scene, get_uid, … | "4.4+ for UID tools"; 4.7 not mentioned | `claude mcp add godot -e GODOT_PATH=… -- npx @coding-solo/godot-mcp` | Debug output only; no screenshots or input |
| [hi-godot/godot-ai](https://github.com/hi-godot/godot-ai) | 2828 | v4.3.0, 2026-10-03 | Python (uvx) + GDScript addon | **Yes** | 46 tools / 120+ ops: scene/node/script/test_run/logs_read/editor_screenshot/game_manage … | **"Godot 4.7+" for v4** | Addon's dock **Configure** button writes the client config (`godot-ai attach`); needs `uv` | Yes: viewport and game screenshots, runtime tree, key/mouse/action input |
| [yurineko73/Godot-MCP-Native](https://github.com/yurineko73/Godot-MCP-Native) | 831 | v1.0.8, 2026-07 | Pure GDScript addon (HTTP :9080) | Yes, but can launch as `godot --editor … -- --mcp-server` | 155 | "4.x, 4.5+ recommended" | None given; HTTP transport implied | Editor screenshot, debugger, runtime probe |
| [youichi-uda/godot-mcp-pro](https://github.com/youichi-uda/godot-mcp-pro) | 617 | v1.17.1, 2026-09-24 | Node (closed, **paid $15**) + addon | Yes | 187 (README) / 162 (description) | some tools "4.7+" | `.mcp.json` → `node …/index.js` | Yes: screenshots, compare, simulate input |
| [ee0pdt/Godot-MCP](https://github.com/ee0pdt/Godot-MCP) | 617 | **2025-03-19 (stale)** | Node + addon | Yes | ~21 | none | Claude Desktop only | No |
| [tugcantopaloglu/godot-mcp](https://github.com/tugcantopaloglu/godot-mcp) | 473 | v3.1.0, 2026-07-13 | Node (build from source) + optional autoload (TCP :9090) | **No** | 157 | **"tested and working with 4.7"** | JSON `mcpServers` → `node …/build/index.js` | Yes, via the autoload you add: screenshot, eval, input |
| [tomyud1/godot-mcp](https://github.com/tomyud1/godot-mcp) | 433 | v0.6.0, 2026-08-24 | Node (npx) + addon | Yes | 42 or 75 (README contradicts itself) | "4.x" | `claude mcp add godot -- npx -y godot-mcp-server` | Errors only |
| [IvanMurzak/Godot-MCP](https://github.com/IvanMurzak/Godot-MCP) | 269 | v0.25.1, 2026-09 | **C# addon: needs the .NET Godot build** + cloud login | Yes | 42 | 4.3+ | `godot-cli setup-mcp claude-code` | — **Not usable with standard GDScript Godot** |
| [satelliteoflove/godot-mcp](https://github.com/satelliteoflove/godot-mcp) | 172 | v4.1.x, push 2026-10-02 | Node (npx) + addon + debugger bridge | Yes | 21 tools / 86 actions; split read and write tools; `--read-only` | "4.5+" | `.mcp.json` → `npx -y @satelliteoflove/godot-mcp`, then `--install-addon` | Yes: screenshots, input, runtime state, frame stepping |
| [GDAI MCP](https://gdaimcp.com) (3ddelano) | 101 | 2026-09-11 | Python (uv) + addon, **paid $19**, closed | Yes | 31 | "4.1+" / "4.2+" | `claude mcp add gdai-mcp uv run …/gdai_mcp_server.py` | Screenshots; input per vendor |
| [wgt19861219/godot-mcp-enhanced](https://github.com/wgt19861219/godot-mcp-enhanced) | 99 | v0.33.1, 2026-09/10 | Node (npx) + addon + game bridge | No (headless tier is the default) | 46 / 240+ actions, descriptions in Chinese only | "4.5–4.7 compat matrix" | `claude mcp add godot -- npx -y godot-mcp-enhanced` | Yes |
| [Erodenn/godot-mcp-runtime](https://github.com/Erodenn/godot-mcp-runtime) | 83 | v3.8.1, 2026-09 | Node (npx), **no addon**; injects a temporary autoload | **No** | ~40: run/attach, take_screenshot, simulate_input, get_scene_tree … | "4.x" | JSON `mcpServers` → `npx -y godot-mcp-runtime` + `GODOT_PATH` | Yes |
| [ryanmazzolini/minimal-godot-mcp](https://github.com/ryanmazzolini/minimal-godot-mcp) | 47 | 2026-09 | Node (npx) | Needs the editor's LSP/DAP ports; a headless editor may do (§1.7, untested) | 4: get_diagnostics, scan_workspace_diagnostics, get_console_output, clear | "3.2+ / 4.x" | JSON for `~/.claude.json` | No |

Also seen but not studied in depth:
- bradypp/godot-mcp (stale since 2025-05), LeeSinLiang (no license, 11 stars), Dokujaa (no license), DaxianLee (Chinese, last commit 2026-01).
- The archived n24q02m/better-godot-mcp.
- FlamxGames/godot-ai-assistant-hub, an in-editor chat plugin rather than an MCP server.

**Takeaways:**
- **The most popular server does no more than the CLI.** Coding-Solo has by far the most stars, but it wraps the same commands an agent can run in Bash.
- **The real value of an MCP is the running game and the live editor:** screenshots, input and the live scene tree. hi-godot/godot-ai is the strongest maintained option for that: MIT, very active, explicitly 4.7+.
  - It needs the editor open.
  - Its **telemetry is on by default**; opt out with `GODOT_AI_DISABLE_TELEMETRY=true`.
- **Headless options that can still see the game:** Erodenn/godot-mcp-runtime and tugcantopaloglu. Both are smaller projects.

---

## 4. Implications for the boilerplate

### 4.1 Recommended agent verification loop (headless, no MCP)

Wrap these steps in project scripts or skills so agents never hand-assemble flags:

1. **After pulling or adding assets:** `godot --headless --path . --import`.
   - It's needed before any check that touches `class_name`.
   - Don't trust its exit code alone, because of the crash at exit (§1.2).
2. **After editing GDScript:**
   - Run gdtoolkit lint on edit, as already planned.
   - Then run a **whole-project compile check**: `godot --headless --path . -s res://tools/check_scripts.gd` (pattern in §1.1). It exits non-zero on failure (verified on macOS). Linux is expected to behave the same, because `quit(n)` is the same path gdUnit4 uses for its exit codes, but I did not run it there. It also avoids the autoload false positive.
   - Don't use bare `--check-only` as the gate: its exit code is wrong on macOS and it fails on every autoload reference.
3. **Logic changes:** `addons/gdUnit4/runtest.sh --headless -a res://test --ignoreHeadlessMode`. 0 means pass. 100, 101 or 103 means look at the output or `reports/*/results.xml`.
4. **Smoke run:** `godot --headless --path . --quit-after 300 --log-file <abs>`, then fail if the log matches `^(SCRIPT )?ERROR`. The exit code alone will not catch runtime errors.
5. **Visual check (opt-in, local Mac only):** `godot --path . --scene res://… --write-movie <tmp>/f.png --quit-after 30`, then the agent reads the last PNG. It needs a window, never headless.
6. **Never pass `-d`** in automated runs without `--remote-debug tcp://127.0.0.1:0`.

For CI (ticket 03 and the CI build ticket):
- Run the same steps on Linux, where exit codes behave.
- Install the exact `4.7.2.stable` web templates, since the lookup path is version-exact.
- Run `--import` before export.

### 4.2 Should we adopt an MCP?

**No MCP should be required.**
- Steps 1–6 cover what agents need day to day.
- The jam workflow promise is "headless is supported, never required." Requiring an MCP would add install steps (Node, uv, an addon) for everyone.

**Document one optional server for sessions where a human has the editor open and wants the agent to see or drive the live game:**
- **hi-godot/godot-ai** is the strongest maintained candidate, by README claims only:
  - MIT, very active, explicitly targets 4.7+.
  - Screenshots, runtime tree, input simulation, logs.
- Before writing it into the guidance, run a one-hour spike on 4.7.2:
  - install it,
  - confirm the Claude Code wiring,
  - turn telemetry off,
  - check that its addon coexists with gdUnit4 and LimboConsole,
  - decide whether the addon gets vendored, or each user installs it.
- **Fallbacks if it disappoints:**
  - satelliteoflove/godot-mcp, which has read-only tool separation and is 4.5+.
  - A headless runtime option, Erodenn/godot-mcp-runtime, for agents without an open editor.
- **Avoid:**
  - Paid or closed servers (Pro, GDAI).
  - IvanMurzak, which needs the .NET build.
  - Stale or unlicensed forks.

### 4.3 What stays a human-in-the-editor task

- Judging the soft/cute look, lighting and shader tuning in Compatibility. Agents can capture frames, but a person decides whether it looks right.
- UI layout and anchors, and scene composition beyond simple programmatic node adds.
- Asset import-setting tuning, and creating the first export preset.
- Playtesting mouse feel and game feel.
- Interactive debugging with breakpoints, the remote scene tree, and the profiler.

---

## Sources

**Godot**
- Docs, 4.7 command-line tutorial: https://docs.godotengine.org/en/stable/tutorials/editor/command_line_tutorial.html
- Source at tag `4.7.2-stable`:
  - `main/main.cpp` (`check_only` handling)
  - `platform/linuxbsd/godot_linuxbsd.cpp`
  - `platform/macos/os_macos.mm` (`OS_MacOS_Headless::run`)
- Release `4.7.2-stable` (published 2026-08-18) assets, via `gh api`.
- Issues: godotengine/godot#78587, #111515, #117123.
- Release notes, checked for MCP or AI: https://godotengine.org/releases/4.5/, /4.6/, /4.7/

**gdUnit4**
- Docs: https://godot-gdunit-labs.github.io/gdUnit4/latest/advanced_testing/cmd/
- Source at `v6.2.1`: `addons/gdUnit4/runtest.sh` and `src/core/runners/GdUnitTestCIRunner.gd`.

**MCP servers**
- Each repo's README and its `gh api` metadata (links in the table).
- https://gdaimcp.com for GDAI.
