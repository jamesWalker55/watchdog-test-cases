from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
import time
from datetime import datetime


class StoredEventHandler(FileSystemEventHandler):
    """Stores all the events captured."""

    def __init__(self) -> None:
        super().__init__()
        self.events = []

    def on_any_event(self, event):
        self.events.append(event)
        return super().on_any_event(event)


class QuickObserver:
    """Use a context manager to automate starting and stopping of
    the observer. For example:

    ```
    with QuickObserver(".") as ob:
        os.mkdir("test_dir")
        with open("test_dir/a.txt", "w") as f:
            pass

    print(ob.events)
    ```

    After leaving the context, access the events through `ob.events`

    Argument `stop_delay` is used to pause execution for some seconds
    on `__exit__` to wait the observer to detect fs changes
    """

    def __init__(self, monitor_path, stop_delay=2):
        super().__init__()

        self._events = None
        self._context_exited = False
        self._monitor_path = monitor_path
        self._stop_delay = stop_delay

    @property
    def events(self):
        if not self._context_exited:
            raise Exception("`event` can only be accessed after leaving context!")
        return self._events

    def __enter__(self):
        self._event_handler = StoredEventHandler()
        self._observer = Observer()
        self._observer.schedule(self._event_handler, self._monitor_path, recursive=True)
        self._context_exited = False
        self._observer.start()
        return self

    def __exit__(self, exc, value, tb):
        time.sleep(self._stop_delay)
        self._context_exited = True
        self._events = self._event_handler.events
        self._observer.stop()
        self._observer.join()


def timestamp_now():
    return datetime.now().strftime("%Y%m%d_%H%M%S_%f")


PREFIX_MAP = {
    "created": "Create",
    "modified": "Modify",
    "deleted": "Delete",
    "moved": "Move  ",
    "closed": "Close "
}


def event_to_log(event: FileSystemEvent, relative_to: Path = None):
    if event.event_type in PREFIX_MAP:
        action = PREFIX_MAP[event.event_type]
    else:
        action = event.event_type
    item = "dir " if event.is_directory else "file"
    if event.event_type == "moved":
        src = Path(event.src_path)
        dest = Path(event.dest_path)
        if relative_to:
            src = src.relative_to(relative_to)
            dest = dest.relative_to(relative_to)
        return f"{action} {item}: {src} -> {dest}"
    else:
        src = Path(event.src_path)
        if relative_to:
            src = src.relative_to(relative_to)
        return f"{action} {item}: {src}"


def generate_report(
    title: str, events: list[FileSystemEvent], relative_to: Path = None
):
    if relative_to:
        lines = [timestamp_now(), title] + [event_to_log(e, relative_to) for e in events]
    else:
        lines = [timestamp_now(), title] + [event_to_log(e) for e in events]
    return "\n".join(lines)
