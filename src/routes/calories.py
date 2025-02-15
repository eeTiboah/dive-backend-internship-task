from fastapi import APIRouter, status, Query, Depends
from src.core.exceptions import ErrorResponse
from src.service.nutrixion import get_nutrition_data
from src.db.database import get_db
from sqlalchemy.orm import Session
from src.models.calories import (
    Calorie,
    CalorieEntry,
    CalorieInput,
    CaloriePaginate,
    CaloriePaginatedResponse,
    CalorieResponse,
    CalorieUpdateInput,
)
from src.utils.oauth2 import get_current_user
from sqlalchemy import desc
from src.db import models
from src.utils.utils import RoleChecker
from src.core.configvars import env_config
from src.db.repository.calorie import create_new_calorie_entry
from datetime import datetime
from src.utils.calorie_utils import (
    check_for_calorie_and_owner,
    delete_calorie_entry,
    get_total_number_of_calories,
    update_calorie_entry,
    build_calorie_query,
)
from typing import Union

calorie_router = APIRouter(tags=["Calorie"], prefix="/calories")

calorie_link = "/api/v1/calories"
allow_operation = RoleChecker(["user", "admin"])


@calorie_router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=CaloriePaginatedResponse,
    dependencies=[Depends(allow_operation)],
)
def get_calories(
    number_of_calories: int = None,
    is_below_expected: bool = None,
    date: str = None,
    order: str = None,
    text: str = None,
    limit: int = Query(default=10, ge=1, le=100),
    page: int = Query(default=1, ge=1),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Return all calorie entries that belong to the current user or all entries if current user is admin
    Query Parameters:
        current_user: The current user object
        db: Database session
        limit: The number of items to display in a page`
        page: The page number

    Return: All calorie entries

    """

    query = build_calorie_query(db, 
                                is_below_expected, 
                                text, 
                                number_of_calories, 
                                date,
                                order)

    calorie_entries = None
    total_calorie_entries = 0

    offset = (page - 1) * limit

    if current_user.role.name == "admin":
        total_calorie_entries = query.count()
        calorie_entries = (
            query
            .offset(offset)
            .limit(limit)
            .all()
        )
    else:
        total_calorie_entries = query.filter(
            models.CalorieEntry.user_id == current_user.id
        ).count()
        calorie_entries = (
            query.filter(models.CalorieEntry.user_id == current_user.id)
            .offset(offset)
            .limit(limit)
            .all()
        )

    pages = (total_calorie_entries - 1) // limit + 1
    calories_response = [
        Calorie(
            date=calorie.date,
            time=calorie.time,
            text=calorie.text,
            number_of_calories=calorie.number_of_calories,
            is_below_expected=calorie.is_below_expected,
        )
        for calorie in calorie_entries
    ]

    links = {
        "first": f"{calorie_link}?limit={limit}&page=1",
        "last": f"{calorie_link}?limit={limit}&page={pages}",
        "current_page": f"{calorie_link}?limit={limit}&page={page}",
        "next": None,
        "prev": None,
    }

    if page < pages:
        links["next"] = f"{calorie_link}?limit={limit}&page={page + 1}"

    if page > 1:
        links["prev"] = f"{calorie_link}?limit={limit}&page={page - 1}"

    response = CaloriePaginate(
        calorie_entries=calories_response,
        total=total_calorie_entries,
        page=page,
        size=limit,
        total_pages=pages,
        links=links,
    )

    return CaloriePaginatedResponse(data=response, errors=[], status_code=200)


@calorie_router.get(
    "/{calorie_id}",
    status_code=status.HTTP_200_OK,
    response_model=CalorieResponse,
    dependencies=[Depends(allow_operation)],
)
def get_calorie(
    calorie_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Returns the calorie entry with the specified id
    Query Parameters:
        calorie_id: The id of the calorie entry to access from db
        current_user: The current user object
        db: Database session

    Return: The calorie entry that corresponds to the Calorie model

    """

    calorie_entry = check_for_calorie_and_owner(
        db,
        calorie_id,
        current_user,
        env_config.ERRORS.get("CALORIE_NOT_FOUND"),
    )
    return_data = calorie_entry.first()
    response = Calorie(
        date=return_data.date,
        time=return_data.time,
        text=return_data.text,
        number_of_calories=return_data.number_of_calories,
        is_below_expected=return_data.is_below_expected,
    )
    return CalorieResponse(data=response, errors=[], status_code=200)


@calorie_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=CalorieResponse,
    dependencies=[Depends(allow_operation)],
)
def create_calorie(
    calorie_entry: CalorieEntry,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Creates a new calorie entry
    Query Parameters:
        calories_entry: Details of the calorie entry to save
        current_user: The current user object
        db: Database session

    Return: A new calorie entry that corresponds to the Calorie model

    """

    nf_calories = 0
    date = datetime.now().date()
    time = datetime.now().time().strftime("%H:%M:%S")

    total_calories_today = get_total_number_of_calories(db, current_user, date)

    if calorie_entry.number_of_calories is None:
        nf_calories = get_nutrition_data(calorie_entry.text)

    number_of_calories = nf_calories or calorie_entry.number_of_calories

    is_below_expected = (
        total_calories_today + number_of_calories
    ) < current_user.expected_calories

    calorie = CalorieInput(
        date=date,
        time=time,
        text=calorie_entry.text,
        number_of_calories=number_of_calories,
        user_id=current_user.id,
        is_below_expected=is_below_expected,
    )

    new_calorie_entry = create_new_calorie_entry(calorie, db)

    response = Calorie(
        date=new_calorie_entry.date,
        time=new_calorie_entry.time,
        text=new_calorie_entry.text,
        number_of_calories=new_calorie_entry.number_of_calories,
        is_below_expected=new_calorie_entry.is_below_expected,
    )

    return CalorieResponse(data=response, errors=[], status_code=201)


@calorie_router.patch(
    "/{calorie_id}",
    status_code=status.HTTP_200_OK,
    response_model=CalorieResponse,
    dependencies=[Depends(allow_operation)],
)
def update_calorie(
    calorie_id: int,
    calorie_entry: CalorieUpdateInput,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Update a calorie entry
    Query Parameters:
        calorie_id: The id of the calorie entry to update
        calorie_entry: The new details to update the calorie entry in the db
        db: Database session
        current_user: The current user object

    Return: The updated calorie entry

    """

    calorie = update_calorie_entry(calorie_id, calorie_entry, db, current_user)

    return calorie


@calorie_router.delete(
    "/{calorie_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(allow_operation)],
)
def delete_calorie(
    calorie_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Delete a calorie entry
    Query Parameters:
        calorie_id: The id of the calorie entry to update
        db: Database session
        current_user: The current user object

    Return: Nothing

    """

    delete_calorie_entry(db, calorie_id, current_user)


@calorie_router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_calories(
    db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    """
    Deletes all calorie entries
    Query Parameters:
        db: Database session

    Return: Nothing

    """

    if current_user.role.name != "admin":
        raise ErrorResponse(
            data=[],
            errors=[{"message": env_config.ERRORS.get("NOT_PERMITTED")}],
            status_code=status.HTTP_403_FORBIDDEN,
        )

    db.query(models.CalorieEntry).delete()
    db.commit()
