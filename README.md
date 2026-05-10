# Opus Magnum Sum Auto Calculator

A small cli-tool to calculate the sum record for new solutions for Opus Magnum by Zachtronics.

## Installation
**Currently only works on Windows**

- Use `pip install -r requirements.txt` to install required packages (globally or in a virtual env).
- Put [om.py](http://critelli.technology/om.py) by panic next to this script (TODO: make a flag to specify location instead.)

If you want windows-toasts to be displayed over your game, turn off "Do Not Disturb" and go to 
**Settings > System > Notifications > Focus Assist** and turn off\
"When I'm playing a game" and "When I'm using an app in full screen mode"

## Usage
Run `python om-sum-autocalc.py`. The script is now running and waiting for changes in the solutions directory
(~\Documents\My Games\Opus Magnum\ on Windows).

Stop with `CTRL+C` 

## ToDo's
In no specific order. Feel free to open issues if you have any suggestions or find bugs.

- Add flag to specify om.py location
- Add flag to disable toasts
- Support for linux (feel free to fork for mac)
- Compare to other local solutions
- Auto-check against online leaderboard for new record

