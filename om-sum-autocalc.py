import re
import sys
import time

from datetime import datetime, timedelta
from pathlib import Path

from watchdog.events import FileSystemEventHandler, DirModifiedEvent, FileModifiedEvent, RegexMatchingEventHandler
from watchdog.observers import Observer
from win11toast import toast, notify

# Put om.py by panic next to this file
import om


class ChangeHandler(FileSystemEventHandler):
    LATENCY_FOR_AVOIDING_DOUBLECHECK = 5

    def __init__(self):
        self.last_modified = datetime.now()

    def on_modified(self, event: DirModifiedEvent | FileModifiedEvent) -> None:
        if event.event_type == ("modified") and not event.src_path.endswith("save.dat"):      # trigger only once
            if datetime.now() - self.last_modified < timedelta(seconds=self.LATENCY_FOR_AVOIDING_DOUBLECHECK):
                return
            else:
                self.last_modified = datetime.now()
            calculate_new_sum(event.src_path)


def extract_puzzle_name(solution_name: str) -> str:
    match = re.match("([a-zA-Z]*-?)*", solution_name)
    if match is None:
        raise ValueError(f"Invalid solution name: {solution_name} -> no puzzle name extractable.")
    text_only = match.group(0)[:-1].replace("-", " ")
    return text_only.title()


def calculate_new_sum(path: str) -> None:
    try:
        solve = om.Solution(path)
        if solve.solved:
            sum3 = solve.cycles + solve.cost + solve.area
            sum4 = sum3 + solve.instructions
            solution_name = Path(path).name
            puzzle_name = extract_puzzle_name(solution_name)
            solution_output_string = (f"New solution for {solution_name}:\n"
                                      f"sum3: {sum3}, sum4: {sum4}")
            print(solution_output_string)
            toast(f"{puzzle_name}", f"sum3: {sum3}, sum4: {sum4}", scenario="reminder", on_dismissed=lambda *args: None)
    except ValueError as e:
        print(f'om.py threw an Exception, probably harmless: {e}', file=sys.stderr)
        # om.py shows a value error if script is started before Opus Magnum.
    except PermissionError as e:
        print(f'Tried to open file while still in use by system: {path}')


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