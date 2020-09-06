import subprocess
import sys

def build_game(n):
    if n == 0:
        subprocess.call(r"python -m PyInstaller --debug bootloader --icon=res/icon/game_icon.ico --add-data config.json;. --add-data res/bg/*;res/bg --add-data res/icon/*;res/icon --add-data res/sprites/*;res/sprites --add-data res/sounds/*;res/sounds play.py")
        print('Done build with bootloader debug')
    elif n == 1:
        subprocess.call(r"pyinstaller --windowed --icon=res/icon/game_icon.ico --add-data config.json;. --add-data res/bg/*;res/bg --add-data res/icon/*;res/icon --add-data res/sprites/*;res/sprites --add-data res/sounds/*;res/sounds play.py")
        print('Done clean build')
    elif n == 2:
        subprocess.call(r"pyinstaller --windowed --icon=res/icon/game_icon.ico --onefile --add-data config.json;. --add-data res/bg/*;res/bg --add-data res/icon/*;res/icon --add-data res/sprites/*;res/sprites --add-data res/sounds/*;res/sounds play.py")
        print('Done build single executable')
    else:
        print('Invalid build number.')

args = sys.argv
if len(args) > 1:
    build_game(int(args[1]))
else:
    print('Build options:\n0 - Debug\n1 - clean\n2 - single executable')
    build_game(int(input()))


