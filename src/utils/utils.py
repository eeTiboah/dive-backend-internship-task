
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, password):
    return pwd_context.verify(plain_password, password)

def handle_errors(err):
    error_list = []
    for error in err():
        field, message = error.get("loc")[1], error.get("msg")
        error_list.append({f"{field}": f"{message}"})

    return error_list