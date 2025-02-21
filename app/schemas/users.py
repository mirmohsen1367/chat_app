import datetime

from pydantic import AfterValidator
from pydantic import BaseModel

from app.schemas.base import CitySchema, ProvinceResponse

from ..validations.user_profile_validation import CreateUserValidation
from typing import List, Annotated


class RequestDetails(BaseModel):
    phone_number: Annotated[
        str, AfterValidator(CreateUserValidation.validate_phone_number)
    ]
    password: str


class TokenSchema(BaseModel):
    access_token: str


class ProfileResponse(BaseModel):
    id: int
    username: str
    phone_number: str
    city: CitySchema
    province: ProvinceResponse
    is_active: bool
    is_staff: bool


class PaginatedProfileResponse(BaseModel):
    total: int
    skip: int
    limit: int
    profiles: List[ProfileResponse]


class TokenCreate(BaseModel):
    user_id: str
    access_token: str
    refresh_token: str
    status: bool
    created_date: datetime.datetime
