import time

from watchdog.events import FileSystemEventHandler, DirModifiedEvent, FileModifiedEvent, RegexMatchingEventHandler
from watchdog.observers import Observer
from datetime import datetime, timedelta
from pathlib import Path

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


def calculate_new_sum(path):
    solve = om.Solution(path)
    if solve.solved:
        sum3 = solve.cycles + solve.cost + solve.area
        sum4 = sum3 + solve.instructions
        print(f"New solution {path}: {sum3}, {sum4}")


if __name__ == '__main__':
    handler = ChangeHandler()
    observer = Observer()
    # Intentionally omit steam user ID and use recursive mode
    observer.schedule(handler, Path.home() / 'Documents' / 'My Games' / 'Opus Magnum', recursive=True)
    observer.start()
    print("Observer started, watching for new solutions...")

    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()