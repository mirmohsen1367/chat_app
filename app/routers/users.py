from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_session
from app.helpers.auth_tools import sign_jwt, verify_password
from app.helpers.permissions import is_admin
from app.models.users import User
from app.schemas.users import RequestDetails, TokenSchema

user_router = APIRouter()


@user_router.get("/create_users/")
def create_user(
    dependencies=Depends(is_admin), session: Session = Depends(get_session)
):
    users = session.query(User).all()
    return users


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
