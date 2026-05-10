import re
from pprint import pprint
import time

from datetime import datetime, timedelta
from pathlib import Path
from typing import Tuple

from watchdog.events import FileSystemEventHandler, DirModifiedEvent, FileModifiedEvent, RegexMatchingEventHandler
from watchdog.observers import Observer
from win11toast import toast

# Put om.py by panic next to this file
import om


WINDOWS_APP_ID = "Opus Magnum Sum Calculator"


class ChangeHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_solution: om.Solution = om.Solution()

    def on_modified(self, event: DirModifiedEvent | FileModifiedEvent) -> None:
        if event.event_type == ("modified") and not event.src_path.endswith("save.dat"):      # trigger only once
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
                sum3 = self.calculate_sum(solution)
                if self.last_solution.solved:
                    delta_last = self.calculate_delta(solution, self.last_solution)
                    delta_last_expanded = self.calculate_delta_expanded(solution, self.last_solution)
                    output_string = self.format_output_delta(solution, sum3, delta_last, delta_last_expanded)
                else:
                    output_string = self.format_output(solution, sum3)
                toast(f"{puzzle_name}", output_string, scenario="reminder",
                      audio=True,  # results in silent?
                      app_id=WINDOWS_APP_ID,
                      on_dismissed=lambda *args: None)  # to suppress timeout notification in console

                self.last_solution = solution
        except ValueError as e:
            print(f'om.py threw an Exception, probably harmless: {e}')
            # om.py shows a value error if script is started before Opus Magnum.
        except PermissionError as e:
            print(f'Tried to open file while still in use by system: {path}')
        return None

    def calculate_sum(self, solution: om.Solution) -> int:
        sum3 = solution.cycles + solution.cost + solution.area
        #sum4 = sum3 + solution.instructions
        return sum3

    def calculate_delta(self, solution1: om.Solution, solution2: om.Solution) -> int:
        return self.calculate_sum(solution1) - self.calculate_sum(solution2)

    def calculate_delta_expanded(self, solution1: om.Solution, solution2: om.Solution) -> Tuple[int, int, int]:
        sum3_delta = (solution1.cost - solution2.cost, solution1.cycles - solution2.cycles, solution1.area - solution2.area)
        #sum4_delta = sum3_delta + (solution1.instructions - solution2.instructions)
        return sum3_delta

    # def find_best_with_source_name(self, solution: om.Solution) -> Tuple[om.Solution, str]:
    def format_output_delta(self, solution, sum3, delta_last, delta_expanded):
        return (f"\u0394last solution:\n"
                f"Sum3: {sum3} ({delta_last:+})\n"
                f"{solution.cost}g({delta_expanded[0]:+})/{solution.cycles}c({delta_expanded[1]:+})"
                f"/{solution.area}a({delta_expanded[2]:+})\n\n"
                f"\u0394best solution:\n")

    def format_output(self, solution, sum3):
        return (f"Sum3: {sum3}\n"
                f"{solution.cost}g/{solution.cycles}c/{solution.area}a")

def extract_puzzle_name(solution_filename: str) -> str:
    # TODO: can I get the display_name from om somehow? Fetching from https://zlbb.faendir.com/swagger-ui seems overkill
    # but I need it to calculate local best
    match = re.match("([a-zA-Z]*-?)*", solution_filename)
    if match is None:
        raise ValueError(f"Invalid solution name: {solution_filename} -> no puzzle name extractable.")
    text_only = match.group(0)[:-1].replace("-", " ")
    return text_only.title()



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