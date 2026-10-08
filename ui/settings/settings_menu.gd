extends Control
## The settings panel: volume sliders and Reduce motion, bound to [code]Settings[/code].
## The main menu and the pause menu each instance it hidden and call [method open].
## Back hides it again.

const DEMO_SFX := preload("res://shared/audio/ui_click.ogg")

# Every assignment to Settings saves the file, so a slider commits when its drag ends,
# not on every step. Wheel and arrow-key changes aren't drags and commit at once.
var _dragging := false

@onready var _volumes: Dictionary[HSlider, StringName] = {
	%MasterSlider: &"master_volume",
	%MusicSlider: &"music_volume",
	%SfxSlider: &"sfx_volume",
}


func _ready() -> void:
	for slider: HSlider in _volumes:
		slider.drag_started.connect(_on_volume_drag_started)
		slider.drag_ended.connect(_on_volume_drag_ended.bind(slider))
		slider.value_changed.connect(_on_volume_value_changed.bind(slider))
	_read_settings()


## Shows the panel with the current settings.
func open() -> void:
	_read_settings()
	show()


func _read_settings() -> void:
	for slider: HSlider in _volumes:
		slider.set_value_no_signal(Settings.get(_volumes[slider]))
	%ReduceMotionButton.set_pressed_no_signal(Settings.reduce_motion)


func _commit(slider: HSlider) -> void:
	Settings.set(_volumes[slider], slider.value)


func _on_volume_drag_started() -> void:
	_dragging = true


func _on_volume_drag_ended(_value_changed: bool, slider: HSlider) -> void:
	_dragging = false
	_commit(slider)
	if slider == %SfxSlider:
		Audio.play_sfx(DEMO_SFX)


func _on_volume_value_changed(_value: float, slider: HSlider) -> void:
	if not _dragging:
		_commit(slider)


func _on_reduce_motion_button_toggled(toggled_on: bool) -> void:
	Settings.reduce_motion = toggled_on


func _on_back_button_pressed() -> void:
	hide()
