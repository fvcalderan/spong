# Spong
In-terminal multiplayer pong-like game made in Python

```
  __                _     _
 / _|_   _____ __ _| | __| | ___ _ __ __ _ _ __
| |_\ \ / / __/ _` | |/ _` |/ _ \ '__/ _` | '_ \
|  _|\ V / (_| (_| | | (_| |  __/ | | (_| | | | |
|_|   \_/ \___\__,_|_|\__,_|\___|_|  \__,_|_| |_|

BSD 3-Clause License
Copyright (c) 2021, Felipe V. Calderan
All rights reserved.
See the full license inside LICENSE file
```

![Image](https://github.com/fvcalderan/spong/blob/main/images/screenshot.png?raw=true)

## Prerequisites
The only prerequisite to run Spong is the `curses` library for Python. If
you run GNU/Linux or macOS, it's very likely that it's already installed. On
Windows, though, unfortunately it's not installed by default and there may not
be a direct equivalent (with the same exact function names and stuff), so I
suggest running Spong on WSL/WSL2.

## Running Spong
There are two different ways to run the game: as host and as guest/client. To
run as host, open the terminal and type:
```
python3 spong.py host [your ip] [port] [player_name]
```
and to run as guest/client:
```
python3 spong.py join [host ip] [port] [player_name]
```
Below is an example of joining a `localhost` game:
```
python3 spong.py join localhost 1234 Skore
```

**NOTE:** it's required that both terminals are at least 80x20 (by default).

## Playing as AI
You can host/join a game as an AI player by naming yourself `AI`. The
difficulty can be changed inside `AI.py`.

## Modding the game
Just modify `spong.py` as you like. Remember that, even though Spong can be ran
with 2 different source codes, incompatibilities might break the game, so it's
better if both players have the same version.

A very simple modification that can be done is changing the dimensions of the
board by modifying the values of `SCR_H` and `SCR_W`. This will require a
smaller or bigger terminal depending on the values.

Another possibility is to create new AIs (this is boring, since it's trivial
to create a perfect-playing AI).

## iOS App
It's possible to play Spong using an iOS device as a "remote control". Copy the
files inside `iOS_spong` to your iOS device and load them in `Pythonista 3`.
The iOS version can only join games and the procedure to join is basically the
same as in the terminal version: type the informations requested in the text
boxes and tap the `Connect` button. You can find a screenshot of the App inside
the `images` folder.

## Known bugs
Since this is a very rudimentary implementation of multiplayer, with enough
weirdness going on with TCP messages it's possible that the game loses sync
and breaks (a socket might send/receive too much or too little). It's unlikely
to happen on localhost or local network, though.
