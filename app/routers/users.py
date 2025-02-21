from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_session
from app.helpers.auth_tools import sign_jwt
from app.helpers.filter import ProfileFilter
from app.helpers.helper_func import create_image_media, verify_password
from app.helpers.permissions import is_admin
from app.models.users import Profile, User
from app.schemas.users import (
    # PaginatedProfileResponse,
    RequestDetails,
    TokenSchema,
)
from fastapi import UploadFile, Form, File, Query
from typing import Annotated, Optional

# from sqlalchemy.orm import joinedload

from ..validations.user_profile_validation import (
    CreateUserValidation,
    # UpdateUserValidation,
    CreateProfileValidation,
    # UpdateProfileValidation,
)

# from ..models.base import City, Province
# from decouple import config

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


@user_router.get("")
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
    profiles_list = [
        {
            "id": profile.id,
            "username": profile.user.username,
            "phone_number": profile.user.phone_number,
            "city": {"id": profile.city.id, "name": profile.city.name},
            "province": {"id": profile.province.id, "name": profile.province.name},
            "is_active": profile.user.is_active,
            "is_staff": profile.user.is_staff,
        }
        for profile in profiles
    ]
    return {"total": total, "skip": skip, "limit": limit, "profiles": profiles_list}


# @user_router.get("/{profile_id}/")
# def users_deatil(
#     profile_id: int, _=Depends(is_admin), db: Session = Depends(get_session)
# ):
#     query = (
#         (
#             db.query(Profile)
#             .options(
#                 joinedload(Profile.user),
#                 joinedload(Profile.city),
#                 joinedload(Profile.province),
#             )
#             .order_by(Profile.id.desc())
#         )
#         .filter(Profile.id == profile_id)
#         .first()
#     )


#     profile = query.filter(Profile.id == profile_id).first()
#     if not profile:
#         raise HTTPException(detail="Profile not found", status_code=404)

#     if profile[1]:
#         image = config("HOST", default="http://127.0.0.1:8000") + profile[1]
#     else:
#         image = None
#     return {
#         "image": image,
#         "first_name": profile[2],
#         "last_name": profile[3],
#         "username": profile[4],
#         "phone_number": profile[5],
#         "is_active": profile[6],
#         "is_staff": profile[7],
#         "city": profile[8],
#         "province": profile[9],
#     }


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
    db: Session = Depends(get_session),
    _=Depends(is_admin),
):
    create_user_validation = CreateUserValidation(
        db=db, username=username, phone_number=phone_number, password=password
    )
    user_data = create_user_validation.validate_input_data()
    create_profile_validation = CreateProfileValidation(
        db=db,
        province=province,
        city=city,
        image=image,
        first_name=first_name,
        last_name=last_name,
    )

    user = User(**user_data)
    profile_data = create_profile_validation.validate_input_data()
    profile_data.update({"user": user})
    profile = Profile(**profile_data)
    if "image" in profile_data.keys() and profile_data["image"] is not None:
        create_image_media(
            folder_name=user_data["phone_number"], image=profile_data["image"]
        )
    db.add_all([user, profile])
    db.commit()
    return {"message": "User created successfully"}
