# Opus Magnum Sum Auto Calculator

A small cli-tool to calculate the sum record for new solution.

## Installation
**Currently only works on Windows**

- Use `pip install -r requirements.txt` to install required packages (globally or in a virtual env).
- Put [om.py](http://critelli.technology/om.py) by panic next to this script (TODO: make a flag to specify location instead.)

## Usage
Run `python om-sum-autocalc.py`. The script is now running and waiting for changes in the solutions directory
(~\Documents\My Games\Opus Magnum\ on Windows).

Stop with `CTRL+C` 

## ToDo's
In no specific order. Feel free to open issues if you have any suggestions or find bugs.

- Add flag to specify om.py location
- Support for linux (feel free to fork for mac)
- Show toast
- Compare to other local solutions
- Auto-check against online leaderboard for new record
- Fix error when solution file is in use
- Fix ValueError('unknown version number in solution file') from om.py
