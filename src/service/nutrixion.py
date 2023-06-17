from src.core.configvars import env_config
import httpx
import json
from src.core.exceptions import ErrorResponse
from fastapi import status
from src.service import calorie_cache


def get_nutrition_data(text: str) -> int:
    headers = {
        "x-app-id": f"{env_config.NUTRIXION_APP_ID}",
        "x-app-key": f"{env_config.NUTRIXION_APP_KEY}",
    }
    url = f"{env_config.API_URL}?query={text}"
    timeout = httpx.Timeout(None, read=5.0)
    if calorie_entered := calorie_cache.get_calorie(text):
        return calorie_entered

    resp: httpx.Response = httpx.get(url, headers=headers, timeout=timeout)
    if resp.status_code != 200:
        msg = json.loads(resp.text).get("message")
        raise ErrorResponse(
            data=[],
            errors=[{"message": msg}],
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    data = resp.json()

    branded = data.get("branded")
    if not branded:
        raise ErrorResponse(
            data=[],
            errors=[{"message": env_config.ERRORS.get("ENTRY_NOT_RETRIEVED")}],
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    food = branded[0]

    number_of_calories = food.get("nf_calories")
    calorie_cache.set_calorie(text, number_of_calories)

    return number_of_calories
