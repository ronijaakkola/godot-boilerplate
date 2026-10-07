# Build the Audio and Settings core systems

Type: task
Status: open
Blocked by: 06, 14

## Question

AFK build, per the [core-systems design](06-core-systems-design.md). Use `/tdd` for the logic.

- **Autoloads:** `Events` (`core/events/events.gd`, `piece_placed` only, plus the `##` doc format), `Audio` (`core/audio/`) and `Settings` (`core/settings/`), registered in `project.godot`.
- **Buses:** a `Master`/`Music`/`SFX` bus layout.
- **`Audio`:** `play_music` / `stop_music` with a two-player crossfade, and `play_sfx` on a pool of about 8 players with `pitch_jitter`. It processes always.
- **`Settings`:** typed `master_volume` / `music_volume` / `sfx_volume` / `reduce_motion` with defaults 0.8 / 0.6 / 0.8 / off. Setters apply the value and save `user://settings.cfg`, which is loaded and applied in `_ready()`.
- **Placeholder audio:** CC0 menu loop, UI SFX and placement SFX in `shared/audio/`, with `CREDITS.md`.
- **Tests:** gdUnit4 tests for `Settings` (defaults, round-trip through the cfg, bus volume applied) and `Audio` (same track doesn't restart, pool round robin).

Done when `uv run tools/check.py all` passes.

Note (from ticket 07): built by an agent working under the new guidance (`CLAUDE.md`, `CODING_STANDARDS.md`, the skills). Note any gap or wrong instruction in the guidance as a comment here, so the guidance gets tested in use.
