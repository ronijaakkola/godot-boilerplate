extends GdUnitTestSuite

const GAME := "res://game/game.tscn"


func after_test() -> void:
	get_tree().unload_current_scene()


func test_goto_changes_the_scene() -> void:
	# Named by path: only dev_commands.gd may name LimboConsole.
	get_tree().root.get_node(^"LimboConsole").call("execute_command", "goto " + GAME)
	await await_signal_on(get_tree(), "scene_changed", [], 2000)
	assert_str(get_tree().current_scene.scene_file_path).is_equal(GAME)
