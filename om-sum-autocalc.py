import re
from pprint import pprint
import time

from datetime import datetime, timedelta
from pathlib import Path
from typing import Tuple

import requests
from requests import HTTPError, ConnectionError
from watchdog.events import FileSystemEventHandler, DirModifiedEvent, FileModifiedEvent, RegexMatchingEventHandler
from watchdog.observers import Observer
from win11toast import toast

# Put om.py by panic next to this file
import om


WINDOWS_APP_ID = "Opus Magnum Sum Calculator"
ONLINE_TIMEOUT = 2.0


def extract_puzzle_name(solution_filename: str) -> str:
    # TODO: can I get the display_name from om somehow? Fetching from https://zlbb.faendir.com/swagger-ui seems overkill
    # but I need it to calculate local best
    match = re.match("([a-zA-Z]*-?)*", solution_filename)
    if match is None:
        raise ValueError(f"Invalid solution name: {solution_filename} -> no puzzle name extractable.")
    text_only = match.group(0)[:-1].replace("-", " ")
    return text_only.title()


def solution_sum(solution: om.Solution) -> int:
    sum3 = solution.cycles + solution.cost + solution.area
    #sum4 = sum3 + solution.instructions
    return sum3


def create_delta_dict(solution: om.Solution, delta_solution: om.Solution):
    return {
        'score': solution_sum(delta_solution),
        'delta': solution_sum(solution) - solution_sum(delta_solution),
        'cost': solution.cost - delta_solution.cost,
        'cycles': solution.cycles - delta_solution.cycles,
        'area': solution.area - delta_solution.area
    }


def get_online_url(for_puzzle: str) -> str:
    return f"https://zlbb.faendir.com/om/puzzle/{for_puzzle}/category/SUM/record"


def fetch_online(url: str) -> om.Solution | None:
    online_record_request = requests.get(
        url, headers={"accept": "application/json"}, timeout=ONLINE_TIMEOUT)
    if online_record_request.status_code == 200:
        response = online_record_request.json()
        online_score = response['score']
        artificial_online_solution = om.Solution()
        artificial_online_solution.cycles = online_score['cycles']
        artificial_online_solution.area = online_score['area']
        artificial_online_solution.cost = online_score['cost']
        artificial_online_solution.instructions = online_score['instructions']
        return artificial_online_solution
    else:
        print(f"Warning: Could not fetch online record ({online_record_request.status_code})\n {online_record_request}")
        return None


def format_output(solution, deltas):
    part1 = f"Sum3:\t{solution_sum(solution)}\t\t{solution.cost}g/{solution.cycles}c/{solution.area}a"
    strings = [part1]
    for name, delta in deltas.items():
        s = f"\u0394{name}:\t{delta['score']}({delta['delta']:+})  \t{delta['cost']:+}g/{delta['cycles']:+}c/{delta['area']:+}a"
        strings.append(s)
    return "\n".join(strings)


def windows_toast(title, output):
    toast(f"{title}", output, scenario="reminder", duration="long",
          audio={'silent': 'true'},
          app_id=WINDOWS_APP_ID,
          on_dismissed=lambda *args: None)  # to suppress timeout notification in console


class ChangeHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_solution: om.Solution = om.Solution()

    def test(self):
        print( 'test')

    def on_modified(self, event: DirModifiedEvent | FileModifiedEvent) -> None:
        # print(event)
        if event.event_type == ("modified") and event.src_path.endswith("solution"):      # trigger only once
            self.calculate_new_sum(event.src_path)

    def calculate_new_sum(self, path: str) -> om.Solution | None:
        try:
            solution = om.Solution(path)
            if (solution.solved and (
                    solution.puzzle != self.last_solution.puzzle or
                    solution.cost != self.last_solution.cost or
                    solution.cycles != self.last_solution.cycles or
                    solution.area != self.last_solution.area
                )):
                solution_filename = Path(path).name
                puzzle_name = extract_puzzle_name(solution_filename)
                output = self.create_output(solution)
                print(output, end="\n\n")
                windows_toast(puzzle_name, output)
                self.last_solution = solution
                self.last_solution.source_name = 'last solve'
        except PermissionError as e:
            print(f'Tried to open file while still in use by system: {path}')
        return None

    def create_output(self, solution: om.Solution) -> str:
        deltas = {}
        if self.last_solution.solved:
            deltas['last'] = create_delta_dict(solution, self.last_solution)
        # deltas['best'] = self.create_delta_dict(solution, best_solution)
        try:
            online_solution = fetch_online(get_online_url(solution.puzzle.decode()))
            deltas['online'] = create_delta_dict(solution, online_solution)
        except ConnectionError as e:
            print(f"Could not fetch online: {e}")
        return format_output(solution, deltas)

    def find_local_best(self, solution: om.Solution) -> om.Solution:
       raise NotImplementedError


if __name__ == '__main__':
    handler = ChangeHandler()
    observer = Observer()
    # Intentionally omit steam user ID and use recursive mode
    observer.schedule(handler, Path.home() / 'Documents' / 'My Games' / 'Opus Magnum', recursive=True)
    observer.start()
    print("Observer started, watching for new solutions...")

    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()