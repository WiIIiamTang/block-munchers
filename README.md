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
*Multiplayer is still being worked on.*

In mulitplayer, you can host or connect to a room from the game itself. The server will be hosted at the address specified, `{ip}:{port}` when you enter it in game.

### LAN
Over a local network (**LAN**), **no configuration is necessary**; just enter your name and a port number (like :5555). Then press host, and connect to your own game. Tell your partner to connect to your local ip address, and the same port as well. However, if you're hosting from in-game, just something like ``:5555`` will work. Example:


![https://i.imgur.com/BXrb0SS.gif](https://i.imgur.com/BXrb0SS.gif)

After which, your partner will just need to connect with your local ip address and port.


### Online
To play with someone **not on the same network**, the host player can follow the same process as above, if the server is running on the same network as the game. Host with an empty ip address, and then connect with ``127.0.0.1:{port}``. The other player must connect with the public ip address. Make sure the port is forwarded if needed.

Otherwise, if you're hosting the server somewhere else, both players will have to input the public ip address of the server alongside the port. Make sure your port is forwarded if you need to, and your firewall isn't blocking it either.

 Here are some additional notes about multiplayer:

- Don't use ports that are already in use
- Clicking start (when both players are ready) will start the game for both players, regardless of who is the 'host'
- Aborting the race mode will exit out of the game for both players; you cannot manually quit in multiplayer endless, however.

### Multiplayer game modes
 - Race: Race your friend to the golden blocks at the bottom of the map. **[Currently broken]**
 - Endless: See who can survive the longest in this endless game mode.


# Development
This project is still in development. Cone the repo and install the requirements if needed.
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

Or you could manually build using the .spec files from pyinstaller.

- Singleplayer_levels: Done
- Singleplayer_endless: Done
- ui + cameras: Done
- Index: Done
- Settings: Done
- Multiplayer_backend: In progress
- Multiplayer_gameplay: In progress

# Credits

See ``attributions.txt`` (all free/royalty-free sources) and the license file for music ``License.pdf``.

Made by me
