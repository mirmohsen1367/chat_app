import time

import jwt
from decouple import config
from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext


JWT_SECRET = config("secret")
JWT_ALGORITHM = config("algorithm")


def token_response(token: str):
    return {"access_token": token}


def sign_jwt(user) -> dict:
    payload = {
        "user_id": user.id,
        "username": user.username,
        "phone_number": user.phone_number,
        "expires": time.time() + 36000,
        "is_active": user.is_active,
        "is_staff": user.is_staff,
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token_response(token)


def decode_jwt(token: str) -> dict:
    try:
        decode_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if decode_token["expires"] >= time.time():
            return decode_token
        else:
            return None
    except Exception:
        return {}


password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_hashed_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(password: str, hashed_pass: str) -> bool:
    return password_context.verify(password, hashed_pass)


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(
            JWTBearer, self
        ).__call__(request)
        if credentials:
            if not credentials.credentials.split(" ")[0] in ["Bearer", "jwt"]:
                raise HTTPException(
                    status_code=403, detail="Invalid authentication scheme."
                )
            verify = self.verify_jwt(credentials.credentials.split(" ")[1])
            if not verify:
                raise HTTPException(
                    status_code=403, detail="Invalid token or expired token."
                )
            else:
                return verify

        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    def verify_jwt(self, jwtoken: str) -> bool:
        try:
            payload = decode_jwt(jwtoken)
        except Exception:
            payload = None
        if payload:
            return payload
