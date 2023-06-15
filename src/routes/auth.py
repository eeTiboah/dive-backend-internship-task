
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from src.utils.user_utils import (
    create_new_user,
    get_a_user,
    get_all_users,
)
from src.db import models
from src.db.database import get_db
from src.models.user import (
    User,
    Token,
    UserPaginatedResponse,
    UserResponse,
    TokenResponse,
)
from fastapi.security import OAuth2PasswordRequestForm
from src.utils.utils import verify_password
from src.utils.oauth2 import get_access_token, get_current_user
from src.core.exceptions import ErrorResponse
from src.core.configvars import env_config
from src.utils.utils import RoleChecker


auth_router = APIRouter(tags=["Auth"], prefix="/users")
allow_operation = RoleChecker(["manager", "admin"])


@auth_router.post(
    "/register", status_code=status.HTTP_201_CREATED, response_model=UserResponse
)
def signup(user: User, db: Session = Depends(get_db)):
    
    """
    Route that creates a regular user
    Args:
        user: User schema that is accepted in request
        db: Database session

    Return: The newly created user

    """

    user = create_new_user(user, db)
    return user


@auth_router.post(
    "/login", status_code=status.HTTP_200_OK, response_model=TokenResponse
)
def login(user: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    
    """
    Route that creates a token for authorization
    Args:
        user: Form which accepts a username and a password
        db: Database session

    Return: A JWT Token

    """

    user_data = db.query(models.User).filter(models.User.email == user.username).first()
    if not user_data:
        raise ErrorResponse(
            data=[],
            status_code=status.HTTP_401_UNAUTHORIZED,
            errors=[{"message": env_config.ERRORS.get("INVALID_CREDENTIALS")}],
        )

    if not verify_password(user.password, user_data.password):
        raise ErrorResponse(
            data=[],
            status_code=status.HTTP_401_UNAUTHORIZED,
            errors=[{"message": env_config.ERRORS.get("INVALID_CREDENTIALS")}],
        )

    token, exp = get_access_token(str(user_data.id))

    timestamp = exp.timestamp()

    token_response = Token(token=token, exp=timestamp, token_type="Bearer")

    return TokenResponse(
        data=token_response.dict(), errors=[], status_code=status.HTTP_200_OK
    )


@auth_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(allow_operation)],
    response_model=UserResponse,
)
def create_user(
    user: User, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    """
    Route used by roles to create users
    Args:
        user: The user details to create the user
        current_user: The current user object
        db: Database session

    Return: A user

    """
    get_user_role = current_user.role.name
    if get_user_role == "admin":
        if user.role and user.role.name == "admin":
            raise ErrorResponse(
                data=[],
                errors=[{"message": "You are not allowed to create an admin user"}],
                status_code=status.HTTP_403_FORBIDDEN,
            )

    if get_user_role == "manager":
        if user.role and (user.role.name == "admin" or user.role.name == "manager"):
            raise ErrorResponse(
                data=[],
                errors=[{
                    "message": "You are not allowed to create a user with this role"
                }],
                status_code=status.HTTP_403_FORBIDDEN,
            )

    user = create_new_user(user, db)
    return user


@auth_router.get(
    "/",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(allow_operation)],
    response_model=UserPaginatedResponse,
)
def get_users(
    limit: int = Query(default=10, ge=1, le=100),
    page: int = Query(default=1, ge=1),
    db: Session = Depends(get_db),
):
    """
    Route used by admin role to return all users in the db

    Args:
        db: Database session
        limit: The number of items to display in a page
        page: The page number

    Return: All users

    """

    users = get_all_users(db, page, limit)
    return users

@auth_router.get(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(allow_operation)],
    response_model=UserResponse,
)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Return a user with the specified id
    Query parameters:
        user_id: The id of the user
        db: Database session

    Return: The user in the db

    """

    user = get_a_user(db, user_id)
    return user
