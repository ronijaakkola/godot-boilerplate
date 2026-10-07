# Godot jam boilerplate

The starting project the team clones on jam day: core systems, a main menu and one example game scene, ready to be replaced by the real game.

## Language

**Core system**:
A game-wide service that outlives scene changes and has one instance: the signal bus, audio, scene flow and settings.
_Avoid_: manager, singleton, global

**Signal bus**:
The core system that carries bus events between parts of the game that don't know each other. Named `Events` in code.
_Avoid_: event bus, SignalBus, global signals

**Bus event**:
A past-tense broadcast fact on the signal bus whose emitter neither knows nor cares who listens (e.g. `level_completed`).
_Avoid_: global signal, message

**Command**:
A direct request to a core system to do something (e.g. go to a scene, play a sound). Never a bus event.
_Avoid_: request signal, `*_requested`

**Scene flow**:
The core system that moves the player between top-level scenes (menu → game) with transitions. Named `SceneFlow` in code.
_Avoid_: router, scene manager

**Settings**:
The player's preferences (volumes, mouse sensitivity and similar), kept across sessions. Never game progress. Named `Settings` in code.
_Avoid_: options, config, preferences file

**Save game**:
The player's progress in the game itself. It depends on the game idea, so the boilerplate doesn't have one.
_Avoid_: settings, save file (ambiguous)

**Example game scene**:
The small playable scene that shows the patterns to copy; it is replaced by the real game on jam day.
_Avoid_: demo, sample level

**Visual check**:
A human looking at a change in the editor or browser to judge its feel, which an agent can't sign off on alone.
_Avoid_: QA, review

**Load check**:
Compiling every script in the project at once to catch syntax and type errors before anything runs.
_Avoid_: check-only, compile check

**Smoke run**:
Starting the game briefly without a window and failing if any error is logged, since runtime errors don't stop the game on their own.
_Avoid_: smoke test, headless run
