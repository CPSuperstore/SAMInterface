import json
import os

DEFAULT_PREFERENCES = {
    "recent_files": [],
    "max_recent_files": 10,
    "last_import_dir": None,
    "last_export_dir": None,
    "sam_checkpoint": {
        "model_type": "default",
        "checkpoint_path": "checkpoints/sam_vit_h_4b8939.pth",
        "auto_detect_masks": True
    },
    "export_options": {
        "save_mask_tree": True,
        "save_vector_tree": True,
        "save_raster": True,
        "save_centroids": True,
        "save_detail_mask_tree": True,
        "save_detail_vector_tree": True,
        "save_detail_raster": True,
        "min_area": 5,
        "tolerance": 0.05
    }
}


PREFERENCES_FILE = "preferences.json"


def get_preferences() -> dict:
    try:
        with open(PREFERENCES_FILE) as f:
            loaded = json.loads(f.read())

        write_out = False

        for key, value in DEFAULT_PREFERENCES.items():
            if key not in loaded:
                loaded[key] = value
                write_out = True

        if write_out:
            save_preferences(loaded)

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


def get_sam_checkpoint():
    return get_preferences()["sam_checkpoint"]
