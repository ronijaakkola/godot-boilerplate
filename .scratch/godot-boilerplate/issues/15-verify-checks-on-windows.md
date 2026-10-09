# Verify the checks on Windows

Type: task
Status: resolved
Blocked by: 14

## Question

HITL. Do the checks and hooks from [Build the agent guidance](14-build-agent-guidance.md) work on Windows? On a Windows machine:

1. Clone the repo, install uv and Godot 4.7.2, and set `GODOT` to the `_console.exe` with `setx` (README step 4). Run `git config core.hooksPath .githooks`.
2. Run `uv run tools/check.py all`. It should end with `PASS all`.
3. In Claude Code, have the agent write a `.gd` file with a function named `BadName`. The gdlint problem should come back to the agent as a hook error.
4. Commit that file. `pre-commit` should block the commit.
5. Optionally, run `uv run tools/check.py capture <scene>` once a scene exists.

Record what passed, what failed and the exact error text. Fix what breaks, or write "Windows untested" if nobody can run this before November.

## Answer

The checklist passed on Windows without changes. Extra tests found one bug, a lint hook that silently skipped files when the clone path had non-ASCII characters, and it's fixed (see "Extra tests" below). This was run on 2026-10-09 on Windows 10 Home (19045) with Godot 4.7.2 (`_console.exe`), uv 0.12.3 and Git for Windows 2.51.1, with Claude Code running in PowerShell.

- **Setup:** `setx GODOT` only reaches processes started after it runs, and Claude Code inherits whatever environment the terminal it was launched from had. Restarting Claude Code in the same old terminal still showed `GODOT` as empty. It only worked from a freshly opened terminal. The README's "then open a new terminal" covers this. An older Godot (4.1.1) on the machine didn't interfere, because `check.py` uses only `GODOT`.
- **`check all`:** `PASS lint`, `PASS load: 22 files`, `PASS test: 20 tests`, `PASS smoke: res://ui/main_menu/main_menu.tscn`, `PASS all`.
- **Lint hook:** the agent wrote a `.gd` file with `func BadName()`. The `PostToolUse` hook (`uv run "$CLAUDE_PROJECT_DIR/tools/check.py" lint --hook`) sent back `...windows_lint_probe.gd:4: Error: Function name "BadName" is not valid (function-name)` as a blocking hook error.
- **`pre-commit`:** committing that file failed with exit code 1: `FAIL lint: gdlint found problems` / `pre-commit: fix the lint problems above, then commit again.` No commit was made, and the probe file was removed afterwards.
- **`capture`:** `capture res://ui/main_menu/main_menu.tscn` gave `PASS capture: 60 frames`. The last frame shows the menu as expected.

### Extra tests

These ran in a fresh clone at a 170-character path with a space and umlauts (`…\scratchpad\Tëst dir\Mäkinen boilerplate`).

- **Path length:** the repo's longest tracked path is 89 characters (inside gdUnit4), and the longest `.godot/` cache path is 133. A plain clone failed with `Filename too long`. With `core.longpaths=true`, the clone and `check all` passed, and Godot wrote 9 cache files past 260 characters. This machine has `LongPathsEnabled=1`, so a machine without it is untested. The README now says to clone to a short path or set `core.longpaths`.
- **Non-ASCII path (bug, fixed):** the Claude Code lint hook silently passed a file with `BadName` (exit 0). Python on Windows decodes stdin as cp1252, so the UTF-8 hook JSON turned `Tëst` into `TÃ«st`. The file then looked like it was outside the project, and `lintable()` skipped it. Any teammate with a non-ASCII username would have had no lint hook. `lint <file>` also crashed with `UnicodeEncodeError: 'charmap' codec can't encode character '�'`, because gdlint printed in cp1252 and `check.py` decoded that as UTF-8. The fix in `tools/check.py`: the hook reads `sys.stdin.buffer`, gdlint runs with `PYTHONUTF8=1`, and stdout and stderr are reconfigured to UTF-8. After the fix, the hook exits 2 with the gdlint error, `lint <file>` and `pre-commit` fail cleanly, and `check all` passes in both the umlaut clone and the main repo.
- **`commit-msg`:** `added a probe file` was rejected with the Conventional Commits message, and `chore: add a probe file` was accepted.
- **`pre-merge-commit`:** a non-fast-forward `git merge feature` was blocked. Finishing the merge with `git commit` was then blocked by `pre-commit`'s `MERGE_HEAD` check. `git merge --squash feature` followed by a conventional commit produced a single-parent commit.
- **Line endings:** Git for Windows sets `core.autocrlf=true` system-wide, but `.gitattributes` (`* text=auto eol=lf`) overrides it. A `.gd` and a `.tscn` written with CRLF were stored as LF (`i/lf`). gdlint accepts CRLF. No tracked file is CRLF in the index, and the files Claude Code and Godot wrote this session are LF in the working tree too.
- **Editor round-trip:** saving the scenes in the Windows editor changed every hand-written `.tscn`/`.tres`. It added a header `uid`, a `unique_id` on each node and script uids, and moved one `[connection]` into Godot's order. Nothing else changed. This isn't Windows-specific: `edit-tscn` has agents leave these out, so the first editor save on any OS adds random ones. The user saved all four scenes and `ui/theme.tres`. The agent then added the new uids to the 7 path-only `ext_resource` lines, and `check all` passed. `CODING_STANDARDS.md` now says that when an agent creates a scene or resource, its handoff asks the human to save it in the editor once and commit the result. `core/audio/default_bus_layout.tres` still has no uid; nothing references it by uid.
- **Manual (user, Windows editor and browsers):** the user reported that everything worked: F5 (menu, Play, Esc pause menu, settings surviving a restart), the gdUnit panel's 20 tests, F1 plus `goto` in LimboConsole, and the itch build (music after the start click, Esc in fullscreen, settings after a reload).
- **Previously listed as not tested, now covered by the line above:** F5, the gdUnit panel and F1 for LimboConsole in the Windows editor, and the itch build in Windows browsers.
