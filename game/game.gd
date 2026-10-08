extends Control
## A stand-in for the example game scene, so Play has somewhere to go.

const MAIN_MENU_SCENE := "res://ui/main_menu/main_menu.tscn"


func _on_menu_button_pressed() -> void:
	SceneFlow.go_to(MAIN_MENU_SCENE)
