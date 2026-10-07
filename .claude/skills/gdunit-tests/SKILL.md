---
name: gdunit-tests
description: Write, run and debug gdUnit4 tests in this project. Use when adding or changing tests under test/, testing a scene with simulated mouse or key input, awaiting a signal in a test, or reading a failing `check.py test` run.
---

# gdUnit4 tests

gdUnit4 6.2.1, vendored in `addons/gdUnit4/`. Run every test with `uv run tools/check.py test`.

## Placement

A test mirrors the `res://` path of what it tests, named `<name>_test.gd`:

- `core/settings/settings.gd` → `test/core/settings/settings_test.gd`
- `ui/pause_menu/pause_menu.tscn` → `test/ui/pause_menu/pause_menu_test.gd`

## A suite

```gdscript
extends GdUnitTestSuite

const SCENE := "res://ui/pause_menu/pause_menu.tscn"


func test_open_pauses() -> void:
	var runner := scene_runner(SCENE)
	runner.invoke("open")
	assert_bool(runner.scene().get_tree().paused).is_true()
```

- Every function starting with `test_` is a test. Type everything: an untyped test fails to load.
- `before_test()` / `after_test()` run around each test, `before()` / `after()` once per suite.
- Pick the typed assert: `assert_int`, `assert_float`, `assert_bool`, `assert_str`, `assert_vector`, `assert_array`, `assert_object`, `assert_that`.
- Wrap objects you create with `auto_free(...)` so they're freed after the test. Scenes from `scene_runner` free themselves.

## Testing a scene

`scene_runner(path)` instantiates the scene in the tree and drives frames. Every scene must instantiate on its own, so any scene can be the target.

- `runner.scene()` is the root node. `runner.find_child("Name")` finds a node. `runner.get_property("name")`, `runner.set_property("name", value)` and `runner.invoke("method", args...)` reach into the root script.
- `await runner.simulate_frames(10)` advances frames.

**Mouse input** works headless. Point at a Control's centre and click:

```gdscript
var button := runner.find_child("PlayButton") as Button
runner.set_mouse_position(button.get_global_rect().get_center())
runner.simulate_mouse_button_pressed(MOUSE_BUTTON_LEFT)
await runner.await_input_processed()
```

Keys and actions work the same way: `simulate_key_pressed(KEY_ESCAPE)`, `simulate_action_pressed("pause")`. Ignore the startup warning that input events aren't transported in headless mode; the cases above pass headless. Clicking a 3D object through physics picking is unverified, so test the picking logic by calling the method that handles the click.

## Signals

A signal emitted **during** the call you make (a click, an `invoke`) has already fired before any `await` starts. Start monitoring first, then assert:

```gdscript
monitor_signals(runner.scene())
runner.simulate_mouse_button_pressed(MOUSE_BUTTON_LEFT)
await assert_signal(runner.scene()).is_emitted("clicked", [1])
```

Bus events work the same way: `monitor_signals(Events)` then `await assert_signal(Events).is_emitted("piece_placed", [Vector3.ZERO])`.

A signal that fires **later** (after a timer or a tween) can be awaited directly: `await runner.await_signal("faded_in")`, or `await await_signal_on(node, "finished", [], 2000)` for any object. Both time out after 2 s by default and fail the test.

## Core systems and user://

Autoloads (`Events`, `Audio`, `Settings`, `SceneFlow`) are live during tests and keep their state between tests. Reset what you change in `after_test()`. A test that writes `user://settings.cfg` deletes it in `after_test()` so the next test starts from defaults.

## Reading a failure

`check.py test` prints the full run when it fails:

```
  res://test/core/audio/audio_test.gd > test_same_track_keeps_playing FAILED 3ms
  Report:
  Expecting:
 5
 but was
 4	at 'test_same_track_keeps_playing' in res://test/core/audio/audio_test.gd:12
```

- The two `Remote Debugger` ERROR lines at the top are expected on every run.
- `await_signal_on(...) timed out` means the signal fired before the await, or never. See Signals.
- A test file that fails to parse aborts the whole run with exit code 105 and prints the parse error.
- Exit code 100 means failures. 101 means warnings only, which `check.py` counts as a pass.
- Reports are in `build/reports/report_N/` (HTML and JUnit XML).
