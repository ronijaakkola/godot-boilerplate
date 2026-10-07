# Build the CI pipeline

Type: task
Status: resolved
Blocked by: 05, 08

## Question

AFK. Add `.github/workflows/pr-tests.yml` (gdUnit4-action v1.3.2, `version: installed`, `paths: res://test`) and `.github/workflows/deploy-web.yml` (setup-godot v2.4.3 with `use-dotnet: false` and `include-templates: true`, `--import`, `--export-release "Web"`, butler 15.32.0 push to `${{ vars.ITCH_TARGET }}:html5`), starting from the sketches in the [plugin/CI research](../research/03-plugins-and-ci-compat.md). Make the test job a required check on `main`. Done when a PR runs the tests green on GitHub and a push to `main` shows up playable on itch.io.

Notes:
- `test/` is empty until another ticket adds tests. Check whether gdUnit4-action passes or fails with no suites, and ship one trivial test if it fails.
- After the first push, tick "This file will be played in the browser" on the `html5` upload (ticket 08).

## Comments

- From the core-systems design ticket: `build/` has no `.gdignore`, and the preset's `all_resources` filter packs the previous export's `build/web/*` into the next `.pck` (seen: `res://build/…/index.png` inside the pck). Add `build/.gdignore` (or `build/*` to `exclude_filter`) before CI exports.
- From the agent guidance ticket: CI reuses `uv run tools/check.py` (`lint`, `load`, `smoke`; `test` too if it's simpler than gdUnit4-action) on Linux, so local and CI checks match. It needs uv in the runner and `GODOT` pointing at setup-godot's binary. `tools/*` is already in the Web `exclude_filter`.
- From the itch.io setup ticket: the repo is public at `ronijaakkola/godot-boilerplate`, so making the test job a required check needs no paid plan. `BUTLER_API_KEY` and `ITCH_TARGET=nashtanir/game-off-2026` are already set. The itch page is a draft, so check the deploy while logged in as `nashtanir`.
- Progress (2026-10-07): [PR #1](https://github.com/ronijaakkola/godot-boilerplate/pull/1) (branch `ci/pipeline`) adds both workflows and `build/*` to the Web `exclude_filter` (a second local export is now the same size, with no `res://build/` paths in the pck). The `test` job passed on the PR in 44s with Godot 4.7.2 under xvfb. With an empty `test/`, gdUnit4 prints "No test cases found" and exits 0, and the action's publish step has `fail-on-empty: 'false'`, so no trivial test is needed. **Left for the human**, because the agent was not permitted to do them: make `test` a required check on `main`, squash-merge the PR, confirm the first `deploy-web` run, then tick "played in the browser" on the `html5` upload.
- Open question: once `test` is required, the CLAUDE.md rule "merge with local `git merge --squash`, then push" only works for admins, because a local squash commit has no check runs. Teammates would need to merge on GitHub with "Squash and merge" instead. Decide whether to update CLAUDE.md and the repo's merge settings.

## Answer

Done. Facts later tickets depend on:

- **Workflows** ([PR #1](https://github.com/ronijaakkola/godot-boilerplate/pull/1)): `.github/workflows/pr-tests.yml` (job `test`, gdUnit4-action v1.3.2, `version: installed`, `paths: res://test`) and `.github/workflows/deploy-web.yml` (setup-godot v2.4.3 with templates, `--import`, `--export-release "Web"`, butler 15.32.0 to `${{ vars.ITCH_TARGET }}:html5` with `--if-changed`). Both match the research sketches.
- **Tests on PRs**: green in 44s, running Godot 4.7.2 under xvfb + OpenGL3. With an empty `test/` the runner prints "No test cases found", exits 0, and the publish step doesn't fail (`fail-on-empty: 'false'`). No placeholder test was shipped.
- **Deploy**: the first run on `main` took 53s and pushed a 45 MB build (17.6 MB upload) as the first `html5` build. "Played in the browser" is ticked, and the user confirmed it plays on itch.
- **Required check**: `test` is required on `main` with `enforce_admins: false` and no required PR reviews, so admins can still push directly (the user wants that during build-out). Anyone else needs `test` to pass on the commit, which in practice means a PR.
- **Export hygiene**: the Web `exclude_filter` is now `addons/gdUnit4/*, test/*, build/*`. A second local export no longer packs the previous build.
- **Not done here**: CI doesn't run `check.py` (lint/load/smoke) yet. Handed to Build the agent guidance, since `tools/check.py` doesn't exist yet.
