
from fastapi import FastAPI, Request, status
import logging
from src.core.request_exception import RequestException
from src.core.exceptions import ErrorResponse
from fastapi.responses import JSONResponse
from src.routes.auth import auth_router
from fastapi.exceptions import RequestValidationError
from src.utils.utils import handle_errors

app = FastAPI()


logging.basicConfig(level=logging.DEBUG)

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