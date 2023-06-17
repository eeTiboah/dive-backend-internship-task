import datetime
from typing import Optional


_cache = {}
_value_lifetime = 1.0


def get_calorie(text) -> Optional[dict]:
    data = _cache.get(text)
    if not data:
        return None
    last_saved = data.get("time")
    time_difference = datetime.datetime.now() - last_saved
    if time_difference / datetime.timedelta(minutes=60) < _value_lifetime:
        return data.get("nf_calories")

    del _cache[text]
    return None


def set_calorie(text, nf_of_calories) -> None:
    data = {"time": datetime.datetime.now(), "nf_calories": nf_of_calories}

    _cache[text] = data
