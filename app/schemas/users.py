import datetime

from pydantic import AfterValidator
from pydantic import BaseModel
from typing_extensions import Annotated

from ..helpers.validators import validate_is_strong
from ..helpers.validators import validate_phone_number


class CreateUser(BaseModel):
    phone_number: Annotated[str, AfterValidator(validate_phone_number)]
    password: Annotated[str, AfterValidator(validate_is_strong)]


class RequestDetails(BaseModel):
    phone_number: Annotated[str, AfterValidator(validate_phone_number)]
    password: str


class TokenSchema(BaseModel):
    access_token: str


# class ChangePassword(BaseModel):
#     phone_number: str
#     old_password: str
#     new_password: Annotated[str, AfterValidator(validate_is_strong)]


class UserResponse(BaseModel):
    id: int
    username: str
    phone_number: str
    is_active: bool


class TokenCreate(BaseModel):
    user_id: str
    access_token: str
    refresh_token: str
    status: bool
    created_date: datetime.datetime
