import json
from pathlib import Path

STATE_PATH = Path("states/states.json")


class StateKeys:
    SCRAPED = "scraped"
    CLUSTERED = "clustered"
    S3_UPLOAD_DONE = "s3_upload_done"
    ARTICLESDB_UPLOAD_DONE = "articlesdb_upload_done"


def _load():
    if not STATE_PATH.exists():
        return {}
    with STATE_PATH.open("r") as fh:
        return json.load(fh)


def _save(state):
    STATE_PATH.parent.mkdir(exist_ok=True)
    tmp = STATE_PATH.with_suffix(".tmp")
    with tmp.open("w") as f:
        json.dump(state, f, indent=2)
    tmp.replace(STATE_PATH)


def get(key, default=False):
    return _load().get(key, default)


def set(key, value=True):
    if not isinstance(value, bool):
        raise ValueError("State values must be boolean")

    state = _load()
    state[key] = value
    _save(state)