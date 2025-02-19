import re
from fastapi import HTTPException

from app.models.base import City, Province
from ..models.users import User


def validate_is_strong(value: str) -> str:
    if len(value) < 8:
        raise HTTPException(
            detail="Password must be at least 8 characters long.", status_code=400
        )

    if not any(char.isdigit() for char in value):
        raise HTTPException(
            detail="Password must contain at least one digit.", status_code=400
        )

    if not any(char in "!@#$%^&*()-_=+[]{}|;:',.<>?/" for char in value):
        raise HTTPException(
            detail="Password must contain at least one special character.",
            status_code=400,
        )

    if not any(char.islower() for char in value) or not any(
        char.isupper() for char in value
    ):
        raise HTTPException(
            detail="Password must contain both uppercase and lowercase letters.",
            status_code=400,
        )
    return value


def validate_phone_number(value: str) -> str:
    if not re.match(r"^09\d{9}$", value):
        raise HTTPException(detail="Invalid phone_number", status_code=400)
    return value


def validate_image(value: str) -> str:
    image_file_regex = re.compile(r".*\.(jpg|jpeg|png|gif|bmp)$", re.IGNORECASE)
    if not image_file_regex.match(value):
        raise HTTPException(
            status_code=400,
            detail="Invalid image file type. Allowed formats are jpg, jpeg, png, gif, bmp.",
        )
    return value


def validate_phone_number_exists(db, value):
    phone_number = validate_phone_number(value=value)
    user = db.query(User).filter(User.phone_number == phone_number).first()
    if user is not None:
        raise HTTPException(
            detail="A user with phone_number already exists", status_code=400
        )
    return phone_number


def validate_username_exists(db, value):
    user = db.query(User).filter(User.username == value).first()
    if user is not None:
        raise HTTPException(
            detail="A user with username already exists", status_code=400
        )
    return value


def validate_province_id(db, value):
    province = db.query(Province).filter(Province.id == value).first()
    if province:
        return province
    else:
        raise HTTPException(detail="Province not found", status_code=400)


def validate_city_id(db, province_id, value):
    city = (
        db.query(City).filter(City.id == value, City.province_id == province_id).first()
    )
    if city:
        return city
    else:
        raise HTTPException(detail="City not found", status_code=400)
