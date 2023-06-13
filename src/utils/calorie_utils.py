from src.core.exceptions import NotFoundError, ForbiddenError
from src.db import models
from src.schema.calories import CalorieUpdate, CalorieResponse
from datetime import datetime
from sqlalchemy import func


def get_total_number_of_calories(db, current_user, date):
    total_calories_today = (
        db.query(func.coalesce(func.sum(models.CalorieEntry.number_of_calories), 0))
        .filter(
            models.CalorieEntry.user_id == current_user.id
            and models.CalorieEntry.date == date
        )
        .scalar()
    )

    return total_calories_today


def check_for_calorie_and_owner(db, calorie_id, current_user, msg):
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
        raise NotFoundError(detail="Calorie entry not found")
    if current_user.role.name == "admin":
        return calorie_entry
    elif first_entry.user_id != current_user.id:
        raise ForbiddenError(
            detail=msg,
        )

    return calorie_entry


def update_calorie_entry(calorie_id, calorie_entry, db, current_user):
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
        db, calorie_id, current_user, "You not authorized to update this calorie entry"
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

    return CalorieResponse(
        date=updated_calorie_entry.date,
        time=updated_calorie_entry.time,
        text=updated_calorie_entry.text,
        number_of_calories=updated_calorie_entry.number_of_calories,
        is_below_expected=updated_calorie_entry.is_below_expected,
    )


def delete_calorie_entry(db, calorie_id, current_user):
    """
    Deletes a calorie entry
    Args:
        db: Database session
        calorie_id: The id of the calorie entry to obtain from db
        current_user: The current user object

    Return: Nothing

    """

    calorie = check_for_calorie_and_owner(
        db, calorie_id, current_user, "You not authorized to delete this calorie entry"
    )
    calorie.delete()
    db.commit()
