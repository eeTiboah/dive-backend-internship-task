
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from src.utils.user_utils import (
    create_new_user,
)
from src.db import models
from src.db.database import get_db
from src.models.user import (
    User,
    Token,
    UserResponse,
    TokenResponse,
)
from fastapi.security import OAuth2PasswordRequestForm
from src.utils.utils import verify_password
from src.utils.oauth2 import get_access_token
from src.core.exceptions import ErrorResponse
from src.core.configvars import env_config


auth_router = APIRouter(tags=["Auth"], prefix="/users")

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