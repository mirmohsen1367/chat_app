from fastapi import Depends, HTTPException

from .auth_tools import JWTBearer


def is_admin(user: dict = Depends(JWTBearer())):
    if user.get("is_staff") and user.get("is_active"):
        return True
    raise HTTPException(status_code=403, detail="Only admin can access this")
