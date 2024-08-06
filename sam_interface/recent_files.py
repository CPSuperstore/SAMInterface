import json
import os.path
import typing

RECENT_FILE_PATH = "recent_files.json"
MAX_RECENT_FILES = 10


def get_recent_files() -> typing.List[str]:
    try:
        with open(RECENT_FILE_PATH) as f:
            return json.loads(f.read())

    except FileNotFoundError:
        return []


def add_recent_file(path: str):
    path = os.path.abspath(path)
    recent_files = get_recent_files()

    if path in recent_files:
        recent_files.remove(path)

    recent_files.insert(0, path)

    with open(RECENT_FILE_PATH, 'w') as f:
        f.write(json.dumps(recent_files[:MAX_RECENT_FILES], indent=4))
