# Blockmuncher-game

A 2D block-breaking game made in pygame. Featuring 10 levels, over 10 different types of blocks, endless mode, and multiplayer support for up to 2 players (1v1 mode). 

![https://i.imgur.com/JYMrIsJ.png](https://i.imgur.com/JYMrIsJ.png)


# Quick Start: Playing the game
### Windows
See the [releases]([https://github.com/WiIIiamTang/block-munchers/releases](https://github.com/WiIIiamTang/block-munchers/releases)) page to download the latest version of the game. You can download the zip file or the single executable version.

### Linux
You will need python3 (3.6 or above).
Clone the repo and run ``play.py``.
```
git clone https://github.com/WiIIiamTang/block-munchers.git
cd block-munchers
pip3 install -r requirements.txt
python3 play.py
```

### Navigating the game
- Play
   - Levels: select a level to play.
   - Endless: start a endless game mode.
   - Multiplayer
      - Host or Connect to a multiplayer game. There are two game modes to choose from. Both players must lock in before starting the match.
- Index: View information on the types of blocks in the game.
- Help: Get basic information on how to play.
- Settings: Change framerate and other settings.

# Multiplayer support
The server will be hosted at the address specified, `{ip}:{port}` when you enter it in game.

### LAN
Over a local network (**LAN**), **no configuration is necessary**; just enter your name and a port number (like 5555). Then press host, and connect to your own game. Tell your partner to connect to the same port as well. **You do not need to put an ip address.** Just something like ``:5555`` will work. Example:


![https://i.imgur.com/BXrb0SS.gif](https://i.imgur.com/BXrb0SS.gif)

### Online
To play with someone **not on the same network**, you'll have to input your public ip address alongside the port. Make sure your port is forwarded if you need to. Make sure your firewall isn't blocking it either.

 Here are some additional notes about multiplayer:

- Don't use ports that are already in use (obviously)
- Clicking start (when both players are ready) will start the game for both players, regardless of who is the 'host'
- Aborting the race mode will exit out of the game for both players; you cannot manually quit in multiplayer endless, however.

# Development
Cone the repo and install the requirements if needed.
**To build** the release, run ``build.py``.

This uses pyinstaller to package the files. For a windows release, run ``build.py`` on windows, for Linux, run it on a linux machine, etc.

Resource files (ie. images, sounds) need to be added as data to pyinstaller. ``build.py`` already takes care of this, but if you were to add more folders you would need to add them in.

__Build options__
```
0 - Debug
1 - Clean (prod)
2 - Single exe
3 - Server only
```
#### Customizing game
Some elements that are easy to change:
- Levels are easily modified by editing the ``levels.py`` file. Levels are 2d arrays containing integers; each integer corresponds to a block type (see ``sprites.py``).

 - The endless mode functions by generating 800x800 chunks at a time; you can edit the rates in ``level_constructor.py``.

# Credits

See ``attributions.txt`` (all free/royalty-free sources) and the license file for music ``License.pdf``.

Made by me
