# Build the CI pipeline

Type: task
Status: open
Blocked by: 05, 08

## Question

AFK. Add `.github/workflows/pr-tests.yml` (gdUnit4-action v1.3.2, `version: installed`, `paths: res://test`) and `.github/workflows/deploy-web.yml` (setup-godot v2.4.3 with `use-dotnet: false` and `include-templates: true`, `--import`, `--export-release "Web"`, butler 15.32.0 push to `${{ vars.ITCH_TARGET }}:html5`), starting from the sketches in the [plugin/CI research](../research/03-plugins-and-ci-compat.md). Make the test job a required check on `main`. Done when a PR runs the tests green on GitHub and a push to `main` shows up playable on itch.io.

Notes:
- `test/` is empty until another ticket adds tests. Check whether gdUnit4-action passes or fails with no suites, and ship one trivial test if it fails.
- After the first push, tick "This file will be played in the browser" on the `html5` upload (ticket 08).
