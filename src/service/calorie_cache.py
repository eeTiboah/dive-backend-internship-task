import datetime
from typing import Optional


_cache = {}
_value_lifetime = 1.0


def get_calorie(text: str) -> Optional[dict]:
    """
    Gets the value for a key in a cache
    Args:
        text: The value to search the cache

    Return: A dict or None

    """
    data = _cache.get(text)
    if not data:
        return None
    last_saved = data.get("time")
    time_difference = datetime.datetime.now() - last_saved
    if time_difference / datetime.timedelta(minutes=60) < _value_lifetime:
        return data.get("nf_calories")

    del _cache[text]
    return None


def set_calorie(text: str, nf_of_calories: int) -> None:
    """
    Sets the value in the cache using the text as key with time and nf_calories as values
    Args:
        text: The text to use as key
        nf_of_calories: The number of calories obtained from the API call using the text

    Return: None

    """
    data = {"time": datetime.datetime.now(), "nf_calories": nf_of_calories}

    _cache[text] = data
