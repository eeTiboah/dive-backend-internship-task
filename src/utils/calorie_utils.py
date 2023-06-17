from datetime import datetime
from src.models.calories import (
    Calorie,
    CalorieResponse,
    CalorieUpdate,
    CalorieUpdateInput,
)
from src.db import models
from src.core.configvars import env_config
from fastapi import status
from src.core.exceptions import ErrorResponse
from sqlalchemy import func
from src.db.models import User, CalorieEntry
from sqlalchemy.orm import Session, query


def build_calorie_query(
    db: Session, is_below_expected: bool, text: str, number_of_calories: int, date: str
) -> query.Query:
    query = db.query(models.CalorieEntry)

    if is_below_expected is not None:
        query = query.filter(models.CalorieEntry.is_below_expected == is_below_expected)
    if text is not None:
        query = query.filter(models.CalorieEntry.text == text)
    if number_of_calories is not None:
        query = query.filter(
            models.CalorieEntry.number_of_calories == number_of_calories
        )
    if date is not None:
        query = query.filter(models.CalorieEntry.date == date)

    return query


def get_total_number_of_calories(
    db: Session, current_user: User, date: datetime
) -> int:
    total_calories_today = (
        db.query(func.coalesce(func.sum(models.CalorieEntry.number_of_calories), 0))
        .filter(
            models.CalorieEntry.user_id == current_user.id
            and models.CalorieEntry.date == date
        )
        .scalar()
    )

    return total_calories_today


def check_for_calorie_and_owner(
    db: Session, calorie_id: int, current_user: User, msg: str
) -> CalorieEntry:
    """
    Checks if a calorie entry exists and if it belongs to the current user
    Args:
        db: Database session
        calorie_id: The id of the calorie entry to obtain from db
        current_user: The current user object

    Return: The query object

    """

    calorie_entry = db.query(models.CalorieEntry).filter(
        models.CalorieEntry.id == calorie_id
    )
    first_entry = calorie_entry.first()
    if not first_entry:
        raise ErrorResponse(
            data=[],
            errors=[{"message": env_config.ERRORS.get("CALORIE_NOT_FOUND")}],
            status_code=status.HTTP_404_NOT_FOUND,
        )
    if current_user.role.name == "admin":
        return calorie_entry
    elif first_entry.user_id != current_user.id:
        raise ErrorResponse(
            data=[], errors=[{"message": msg}], status_code=status.HTTP_403_FORBIDDEN
        )

    return calorie_entry


def update_calorie_entry(
    calorie_id: int, calorie_entry: CalorieUpdateInput, db: Session, current_user: User
) -> CalorieResponse:
    """
    Updates a calorie entry
    Args:
        db: Database session
        calorie_id: The id of the calorie entry to obtain from db
        current_user: The current user object
        calorie_entry: The data to be used to update the calorie entry in db

    Return: The query object

    """

    calorie = check_for_calorie_and_owner(
        db,
        calorie_id,
        current_user,
        env_config.ERRORS.get("NOT_PERMITTED_UPDATE_CALORIE"),
    )
    current_time = datetime.utcnow()
    date = datetime.now().date()

    if calorie_entry.number_of_calories:
        entry = (
            db.query(models.CalorieEntry)
            .filter(models.CalorieEntry.id == calorie_id)
            .first()
        )
        total_calories = get_total_number_of_calories(db, current_user, date)

        total_calories_before_update = total_calories - entry.number_of_calories
        updated_total_calories = (
            total_calories_before_update + calorie_entry.number_of_calories
        )

        is_below_expected = updated_total_calories < current_user.expected_calories
        updated_calorie = CalorieUpdate(
            text=calorie_entry.text,
            number_of_calories=calorie_entry.number_of_calories,
            updated_at=current_time,
            is_below_expected=is_below_expected,
        )
    else:
        updated_calorie = CalorieUpdate(
            text=calorie_entry.text,
            number_of_calories=calorie_entry.number_of_calories,
            updated_at=current_time,
        )

    updated_dict = updated_calorie.dict()
    new_update = {k: v for k, v in updated_dict.items() if v is not None}

    calorie.update(new_update)
    db.commit()
    updated_calorie_entry = calorie.first()

    response = Calorie(
        date=updated_calorie_entry.date,
        time=updated_calorie_entry.time,
        text=updated_calorie_entry.text,
        number_of_calories=updated_calorie_entry.number_of_calories,
        is_below_expected=updated_calorie_entry.is_below_expected,
    )

    return CalorieResponse(data=response, errors=[], status_code=200)


def delete_calorie_entry(db: Session, calorie_id: int, current_user) -> None:
    """
    Deletes a calorie entry
    Args:
        db: Database session
        calorie_id: The id of the calorie entry to obtain from db
        current_user: The current user object

    Return: Nothing

    """

    calorie = check_for_calorie_and_owner(
        db,
        calorie_id,
        current_user,
        env_config.ERRORS.get("NOT_PERMITTED_DELETE_CALORIE"),
    )
    calorie.delete()
    db.commit()
