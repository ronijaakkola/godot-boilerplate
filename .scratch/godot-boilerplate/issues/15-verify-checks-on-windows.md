# Verify the checks on Windows

Type: task
Status: open
Blocked by: 14

## Question

HITL. Do the checks and hooks from [Build the agent guidance](14-build-agent-guidance.md) work on Windows? On a Windows machine:

1. Clone the repo, install uv and Godot 4.7.2, and set `GODOT` to the `_console.exe` with `setx` (README step 4). Run `git config core.hooksPath .githooks`.
2. Run `uv run tools/check.py all`. It should end with `PASS all`.
3. In Claude Code, have the agent write a `.gd` file with a function named `BadName`. The gdlint problem should come back to the agent as a hook error.
4. Commit that file. `pre-commit` should block the commit.
5. Optionally, run `uv run tools/check.py capture <scene>` once a scene exists.

Record what passed, what failed and the exact error text. Fix what breaks, or write "Windows untested" if nobody can run this before November.
