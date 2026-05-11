# Opus Magnum Sum Auto Calculator

A small cli-tool to calculate the sum record for new solutions for Opus Magnum by Zachtronics.

![image](https://raw.githubusercontent.com/tnlen/om-sum-autocalc/refs/heads/main/toast_screenshot.png)

## Installation
**Currently only works on Windows**

- Clone this repo.
- Use `pip install -r requirements.txt` to install required packages.
- Put [om.py](http://critelli.technology/om.py) by panic next to this script.

If you want windows notifications to be displayed over OM:
- Turn off "Do Not Disturb" 
- Go to **Settings > System > Notifications > Focus Assist** and turn off:
  - "When I'm playing a game" 
  - "When I'm using an app in full screen mode".


## Usage
Run `python om-sum-autocalc.py`. The script is now running and waiting for changes in the solutions directory
(~\Documents\My Games\Opus Magnum\ on Windows).

Stop with `CTRL+C` 

## ToDo's
In no specific order. Feel free to open issues if you have any suggestions or found a bug.

- Add flag to specify om.py location
- Add flag to disable toasts
- Support for linux (feel free to fork for mac)
- Create small image instead of text for colored deltas (not supported in windows notification texts)

