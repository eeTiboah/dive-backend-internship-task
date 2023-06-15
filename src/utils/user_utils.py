
from sqlalchemy import desc
from src.db import models
from src.models.user import (
    UserPaginate,
    UserPaginatedResponse,
    UserResponse,
    UserRes
)
from src.core.exceptions import ErrorResponse
from src.db.repository.user import save_user
from src.utils.utils import get_password_hash
from src.core.configvars import env_config
from fastapi import status


def check_for_user(db, user_id):
    """
    Checks for the existence of a user in the database
    Args:
        db: Database session
        user_id: The id of the user

    Return: A user query
    """
    user_in_db = db.query(models.User).filter(models.User.id == user_id)
    first_user = user_in_db.first()
    if not first_user:
        raise ErrorResponse(
            data=[],
            errors=[{"message": env_config.ERRORS.get("USER_NOT_FOUND")}],
            status_code=status.HTTP_404_NOT_FOUND,
        )

    return user_in_db



def create_new_user(user, db):
    """
    Creates a regular user
    Args:
        user: User schema that is accepted in request
        db: Database session

    Return: A user

    """

    user_data = db.query(models.User).filter(models.User.email == user.email).first()
    if user_data:
        raise ErrorResponse(
            data=[],
            errors=[{"message": env_config.ERRORS.get("USER_EXISTS")}],
            status_code=status.HTTP_409_CONFLICT,
        )

    hash_passwd = get_password_hash(user.password)
    if user.password != user.password_confirmation:
        raise ErrorResponse(
            data=[],
            errors=[{"message": env_config.ERRORS.get("PASSWORD_MATCH_DETAIL")}],
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    user.password = hash_passwd

    new_user = save_user(user, db)

    data = UserRes(email=new_user.email, 
                   first_name=new_user.first_name, 
                   last_name=new_user.last_name, 
                   role=new_user.role, 
                   expected_calories=new_user.expected_calories)

    return UserResponse(data=data, errors=[], status_code=201)

def get_all_users(db, page, limit):
    """
    Returns all users in the db
    Args:
        db: Database session

    Return: All users

    """

    user_link = "/api/v1/users"

    total_users = db.query(models.User).count()
    pages = (total_users - 1) // limit + 1
    offset = (page - 1) * limit
    users = (
        db.query(models.User)
        .order_by(desc(models.User.created_at))
        .offset(offset)
        .limit(limit)
        .all()
    )

    users_response = [
        UserRes(
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role,
            expected_calories=user.expected_calories,
        )
        for user in users
    ]

    links = {
        "first": f"{user_link}?limit={limit}&page=1",
        "last": f"{user_link}?limit={limit}&page={pages}",
        "current_page": f"{user_link}?limit={limit}&page={page}",
        "next": None,
        "prev": None,
    }

    if page < pages:
        links["next"] = f"{user_link}?limit={limit}&page={page + 1}"

    if page > 1:
        links["prev"] = f"{user_link}?limit={limit}&page={page - 1}"

    response = UserPaginate(
        total=total_users,
        page=page,
        total_pages=pages,
        users_response=users_response,
        links=links,
        size=limit,
    )

    return UserPaginatedResponse(
        data=response, errors=[], status_code=200
    )

def get_a_user(db, user_id):
    """
    Returns user with the specified id
    Args:
        user_id: The id of the user
        db: Database session

    Return: A user

    """

    user = check_for_user(db, user_id).first()

    returned_user = UserRes(
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
        expected_calories=user.expected_calories,
    )
    return UserResponse(data=returned_user, errors=[], status_code=200)