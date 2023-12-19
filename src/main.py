from fastapi import FastAPI, Request, status
from src.core.request_exception import RequestException
from src.core.exceptions import ErrorResponse
from src.routes.auth import auth_router
from src.routes.calories import calorie_router
from src.db import models
from src.models.user import User
from src.core.configvars import env_config
from src.db.models import Role
from src.utils.user_utils import create_new_user
from contextlib import asynccontextmanager
from src.db.database import SessionLocal, Base
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from src.db.database import engine
from sqlalchemy import inspect
import logging

from src.utils.utils import handle_errors


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = SessionLocal()
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    check_tables = bool(tables)
    if not check_tables:
        Base.metadata.create_all(bind=engine)
    try:
        admin = User(
            email=env_config.ADMIN_EMAIL,
            first_name=env_config.ADMIN_FIRST_NAME,
            last_name=env_config.ADMIN_LAST_NAME,
            password=env_config.PASSWORD,
            password_confirmation=env_config.PASSWORD_CONFIRMATION,
            role=Role.admin.name,
        )
        user = db.query(models.User).filter_by(role="admin").first()
        if not user:
            create_new_user(admin, db)
    finally:
        db.close()

    yield
    db.close()


app = FastAPI(lifespan=lifespan)


logging.basicConfig(level=logging.INFO)


@app.get("/")
def index():
    return {"message": "Welcome to Calorie Intake Tracker API"}


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = handle_errors(exc.errors)
    res = RequestException(
        data=[],
        errors=errors,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=res.to_dict(),
    )


async def http_exception_handler(request: Request, exc: ErrorResponse):
    return JSONResponse(status_code=exc.status_code, content=exc.to_dict())


app.add_exception_handler(ErrorResponse, http_exception_handler)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(calorie_router, prefix="/api/v1")
