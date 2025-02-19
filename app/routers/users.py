from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_session
from app.helpers.auth_tools import get_hashed_password, sign_jwt, verify_password
from app.helpers.filter import ProfileFilter
from app.helpers.permissions import is_admin
from app.models.users import Profile, User
from app.schemas.users import (
    PaginatedProfileResponse,
    RequestDetails,
    TokenSchema,
)
from fastapi import UploadFile, Form, File, Query
from typing import Annotated, Optional
from ..helpers.validators import (
    validate_city_id,
    validate_image,
    validate_is_strong,
    validate_phone_number_exists,
    validate_province_id,
    validate_username_exists,
)
from ..config import BASE_DIR
import uuid
from pathlib import Path
import shutil
from ..models.base import City, Province
from decouple import config

user_router = APIRouter()


@user_router.post("/login/", response_model=TokenSchema)
def login(request: RequestDetails, db: Session = Depends(get_session)):
    user = db.query(User).filter(User.phone_number == request.phone_number).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect phone_number"
        )
    if not verify_password(request.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect password"
        )
    access_token = sign_jwt(user)
    return access_token


@user_router.get("", response_model=PaginatedProfileResponse)
def users_list(
    _=Depends(is_admin),
    session: Session = Depends(get_session),
    skip: int = Query(0, description="Number of records to skip (offset)"),
    limit: int = Query(10, description="Number of records to return per page"),
    province: Optional[int] = None,
    city: Optional[int] = None,
    username: Optional[str] = None,
    phone_number: Optional[str] = None,
    is_active: Optional[bool] = None,
    is_staff: Optional[bool] = None,
):
    query = ProfileFilter(db=session).filter(
        username=username,
        phone_number=phone_number,
        province=province,
        city=city,
        is_active=is_active,
        is_staff=is_staff,
    )

    total = query.count()
    profiles = query.offset(skip).limit(limit).all()
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "profiles": [
            {
                "id": profile[0],
                "username": profile[1],
                "phone_number": profile[2],
                "is_active": profile[3],
                "is_staff": profile[4],
                "city": profile[5],
                "province": profile[6],
            }
            for profile in profiles
        ],
    }


@user_router.get("/{profile_id}/")
def users_deatil(
    profile_id: int, _=Depends(is_admin), db: Session = Depends(get_session)
):
    query = (
        db.query(
            Profile.id,
            Profile.image,
            Profile.first_name,
            Profile.last_name,
            User.username,
            User.phone_number,
            User.is_active,
            User.is_staff,
            City.name,
            Province.name,
        )
        .join(User, Profile.user_id == User.id)
        .join(Province, Profile.province_id == Province.id)
        .join(City, Profile.city_id == City.id)
    )

    profile = query.filter(Profile.id == profile_id).first()
    if not profile:
        raise HTTPException(detail="Profile not found", status_code=404)

    if profile[1]:
        image = config("HOST", default="http://127.0.0.1:8000") + profile[1]
    else:
        image = None
    return {
        "image": image,
        "first_name": profile[2],
        "last_name": profile[3],
        "username": profile[4],
        "phone_number": profile[5],
        "is_active": profile[6],
        "is_staff": profile[7],
        "city": profile[8],
        "province": profile[9],
    }


@user_router.post("")
def create_user(
    username: Annotated[str, Form()],
    phone_number: Annotated[str, Form()],
    password: Annotated[str, Form()],
    province: Annotated[int, Form()],
    city: Annotated[int, Form()],
    first_name: Annotated[str, Form()] = None,
    last_name: Annotated[str, Form()] = None,
    image: Annotated[UploadFile, File()] = None,
    session: Session = Depends(get_session),
):
    username = validate_username_exists(session, username)
    phone_number = validate_phone_number_exists(session, phone_number)
    password = validate_is_strong(password)
    province = validate_province_id(session, province)
    city = validate_city_id(session, province_id=province.id, value=city)
    hashed_password = get_hashed_password(password=password)
    user = User(username=username, phone_number=phone_number, password=hashed_password)
    profile_data = {"city": city, "province": province, "user": user}
    if first_name:
        profile_data.update({"first_name": first_name})
    if last_name:
        profile_data.update({"last_name": last_name})
    if image:
        validate_image(image.filename)
        object_folder = BASE_DIR / "media" / f"{phone_number}"
        object_folder.mkdir(parents=True, exist_ok=True)
        unique_filename = f"{uuid.uuid4()}{Path(image.filename).suffix}"
        file_location = object_folder / unique_filename
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        profile_data.update({"image": f"/media/{phone_number}/{unique_filename}"})
    profile = Profile(**profile_data)
    session.add_all([user, profile])
    session.commit()
    return {"message": "User created successfully"}


# @user_router.patch("/{profile_id}/")
# def users_update(
#     profile_id: int, _=Depends(is_admin), db: Session = Depends(get_session)
# ):
#     profile = get_or_404(db, Profile, profile_id)
