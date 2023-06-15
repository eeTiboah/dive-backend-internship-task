from fastapi import Depends, status
from passlib.context import CryptContext
from src.core.exceptions import ErrorResponse
from src.core.configvars import env_config
from src.utils.oauth2 import get_current_user
from src.db.models import User
from typing import List

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    """
    Hashes password
    Args:
        password: The password to be hashed

    Return: The hashed password

    """
    return pwd_context.hash(password)


def verify_password(plain_password, password):
    """
    Verifies password against a hashed one
    Args:
        plain_password: The password entered by the user
        password: The hashed password in the database

    Return: bool

    """
    return pwd_context.verify(plain_password, password)


def handle_errors(err):
    """
    Loops through any errors from the err function call and returns them
    Args:
        err: The err function obtained from RequestValidationError

    Return: List of errors

    """
    error_list = []
    for error in err():
        field, message = error.get("loc")[1], error.get("msg")
        error_list.append({f"{field}": f"{message}"})

    return error_list


class RoleChecker:
    """
    This class is used to check the roles that can access certain routes and perform
    some operations
    """

    def __init__(self, allowed_roles: List):
        """
        This initializes an instance of the RoleChecker class

        Attributes:
            allowed_roles: This is a list that shows the roles allowed to perform certain operations
        """
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_user)):
        """
        This makes an instance of the RoleChecker class callable

        Attributes:
            user: The currently logged in user
        """
        if user.role.name not in self.allowed_roles:
            raise ErrorResponse(
                data=[],
                errors=[{"message": env_config.ERRORS.get("NOT_PERMITTED")}],
                status_code=status.HTTP_403_FORBIDDEN,
            )
