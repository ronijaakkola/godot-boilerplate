# Godot jam game

Godot 4.7.2, GDScript only, Compatibility renderer, played on the web (itch.io) first.

- `CODING_STANDARDS.md`: layout, naming, typing, autoloads, scene composition, signals, merges. Read it before adding or moving any file.
- `DESIGN.md`: what the game is. Read it before gameplay work, and update it when the design changes.
- `CONTEXT.md`: the glossary. Use its terms in code and handoffs.
- `docs/web-constraints.md`: read it before touching shaders, environment, lighting, loading or audio.

## Checks

Run checks exactly as `uv run tools/check.py <command>`. That text is allowlisted, and the script owns every Godot flag.

| Command | When |
|---|---|
| `lint [files]` | Runs by itself after every edit to a `.gd` file; fix what it reports. |
| `load` | After editing scripts, scenes or resources. |
| `test` | After logic changes. |
| `smoke [scene]` | After changes to anything that runs at startup. Runs the main scene, or the one given. |
| `capture <scene>` | After any visual change. Then open the last frame it names and look at it. |
| `all` | Before every handoff. |

## Handoff

- State the result of `uv run tools/check.py all`, with any failing step.
- When a change is about feel (the soft look, lighting, camera, motion, sound), end with "Needs a visual check: `<scene>`".
- When a check can't run (Godot not found, no window for `capture`), say which ones didn't run and name the editor equivalent for the human:

  | Check | In the editor |
  |---|---|
  | `load` | The Output panel's errors after opening the project, or F5 |
  | `test` | The gdUnit panel's run button |
  | `smoke` | F5 (main scene) or F6 (current scene), then the Output panel |
  | `capture` | Run the scene and look at it |

## Agent skills

### Issue tracker

Issues and specs live as local markdown files under `.scratch/<feature-slug>/`. See `docs/agents/issue-tracker.md`.

### Triage labels

Uses the five default triage labels (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`), recorded as a `Status:` line in each issue file. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: one `CONTEXT.md` and `docs/adr/` at the repo root. See `docs/agents/domain.md`.

## Git conventions

- **Commit messages** follow [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/): `<type>(<optional scope>)!: <description>`, with type one of `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`. Example: `feat(player): add double jump`.
- **Merges are squashes.** Merge a branch with `git merge --squash <branch>` followed by one conventional commit. Never create merge commits; use `git pull --rebase` when pulling.

Both rules are enforced by hooks in `.githooks/` (`commit-msg`, `pre-merge-commit`, `pre-commit`). Enable them once per clone with `git config core.hooksPath .githooks`.
