from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_session
from app.helpers.auth_tools import sign_jwt
from app.helpers.filter import ProfileFilter
from app.helpers.helper_func import verify_password
from app.helpers.permissions import is_admin
from app.models.users import Profile, User
from app.schemas.users import (
    RequestDetails,
    TokenSchema,
)
from fastapi import UploadFile, Form, File, Query
from typing import Annotated, Optional

from sqlalchemy.orm import joinedload
from decouple import config
from ..validations.user_profile_validation import user_profile_factory


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
    user_validation_class = user_profile_factory("create_user_validation")
    create_user_validation = user_validation_class(
        db=db, username=username, phone_number=phone_number, password=password
    )

    user_data = create_user_validation.validate_input_data()
    user = User(**user_data)
    profile_validation_class = user_profile_factory("create_profile_validation")
    create_profile_validation = profile_validation_class(
        db=db,
        province=province,
        city=city,
        first_name=first_name,
        last_name=last_name,
        image=image,
        phone_number=phone_number,
    )
    profile_data = create_profile_validation.validate_input_data()
    profile_data.update({"user": user})
    profile = Profile(**profile_data)
    db.add_all([user, profile])
    db.commit()
    return {"message": "User created successfully"}


@user_router.get("/{profile_id}/")
def users_deatil(
    profile_id: int, _=Depends(is_admin), db: Session = Depends(get_session)
):
    query = (
        db.query(Profile)
        .options(
            joinedload(Profile.user),
            joinedload(Profile.city),
            joinedload(Profile.province),
        )
        .order_by(Profile.id.desc())
    ).filter(Profile.id == profile_id)

    profile = query.filter(Profile.id == profile_id).first()
    if not profile:
        raise HTTPException(detail="Profile not found", status_code=404)

    return {
        "image": config("HOST", default="http://127.0.0.1:8000") + profile.image
        if profile.image
        else None,
        "first_name": profile.first_name,
        "last_name": profile.last_name,
        "username": profile.user.username,
        "phone_number": profile.user.username,
        "is_active": profile.user.is_active,
        "is_staff": profile.user.is_staff,
        "city": {"id": profile.city.id, "name": profile.city.name},
        "province": {"id": profile.province.id, "name": profile.province.name},
    }


@user_router.patch("/{profile_id}/")
def update_user(
    profile_id: int,
    username: Annotated[str, Form()] = None,
    phone_number: Annotated[str, Form()] = None,
    password: Annotated[str, Form()] = None,
    province: Annotated[int, Form()] = None,
    city: Annotated[int, Form()] = None,
    first_name: Annotated[str, Form()] = None,
    last_name: Annotated[str, Form()] = None,
    image: Annotated[UploadFile, File()] = None,
    db: Session = Depends(get_session),
    _=Depends(is_admin),
):
    query = (
        db.query(Profile)
        .options(
            joinedload(Profile.user),
            joinedload(Profile.city),
            joinedload(Profile.province),
        )
        .order_by(Profile.id.desc())
    ).filter(Profile.id == profile_id)
    profile = query.filter(Profile.id == profile_id).first()
    if not profile:
        raise HTTPException(detail="Profile not found", status_code=404)
    user = profile.user
    user_validation_class = user_profile_factory("update_user_validation")
    update_user_validation = user_validation_class(
        db=db,
        username=username,
        phone_number=phone_number,
        password=password,
        user=user,
    )
    user_data = update_user_validation.validate_input_data()
    profile_validation_class = user_profile_factory("update_profile_validation")
    update_profile_validation = profile_validation_class(
        db=db,
        province=province,
        city=city,
        first_name=first_name,
        last_name=last_name,
        image=image,
        phone_number=phone_number if phone_number else user.phone_number,
    )
    profile_data = update_profile_validation.validate_input_data()

    if not user_data and not profile_data:
        return {"message": "ok"}

    if user_data:
        for field, value in user_data.items():
            setattr(user, field, value)

    if profile_data:
        for field, value in profile_data.items():
            setattr(profile, field, value)

    db.commit()
    return {"message": "Profile updated successfully."}
