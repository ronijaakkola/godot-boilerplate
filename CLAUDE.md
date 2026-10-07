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
