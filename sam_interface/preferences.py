import json
import os

DEFAULT_PREFERENCES = {
    "recent_files": [],
    "max_recent_files": 10,
    "last_import_dir": None,
    "last_export_dir": None
}


PREFERENCES_FILE = "preferences.json"


def get_preferences() -> dict:
    try:
        with open(PREFERENCES_FILE) as f:
            loaded = json.loads(f.read())

        for key, value in DEFAULT_PREFERENCES:
            if key not in loaded:
                loaded[key] = value

        return loaded

    except FileNotFoundError:
        return DEFAULT_PREFERENCES.copy()


def save_preferences(preferences: dict):
    with open(PREFERENCES_FILE, 'w') as f:
        f.write(json.dumps(preferences, indent=4))


def add_recent_file(path: str):
    path = os.path.abspath(path)

    preferences = get_preferences()
    recent_files = preferences["recent_files"]

    if path in recent_files:
        recent_files.remove(path)

    recent_files.insert(0, path)

    preferences["recent_files"] = preferences["recent_files"][:preferences["max_recent_files"]]
    save_preferences(preferences)


def get_recent_files():
    return get_preferences()["recent_files"]
