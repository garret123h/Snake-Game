import cx_Freeze

executables = [cx_Freeze.Executable("main.py")]

cx_Freeze.setup(
    name="Snake Game",
    options={"build_exe": {"packages": ["pygame"],
                           "include_files": ["./sounds/coin.wav", "./sounds/game_over.mp3",
                                             "./sounds/theme.mp3", "./sounds/06 - Level Theme 2.mp3",
                                             "./sounds/13 - Super Mario Rap.mp3"]}},
    executables=executables

)
