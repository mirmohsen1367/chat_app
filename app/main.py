from fastapi import FastAPI

from app.database import Base, engine

from .routers.base import base_router
from .routers.users import user_router


Base.metadata.create_all(engine)
app = FastAPI()
app.include_router(user_router, prefix="/users", tags=["users"])
app.include_router(base_router, prefix="/base", tags=["base"])
