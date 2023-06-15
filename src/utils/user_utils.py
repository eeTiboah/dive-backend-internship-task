
from src.db import models
from src.models.user import (
    UserResponse,
    UserRes
)
from src.core.exceptions import ErrorResponse
from src.db.repository.user import save_user
from src.utils.utils import get_password_hash
from src.core.configvars import env_config
from fastapi import status


def create_new_user(user, db):
    """
    Creates a regular user
    Args:
        user: User schema that is accepted in request
        db: Database session

    Return: The newly created user

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