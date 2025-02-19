import os
from fastapi import FastAPI
from .routers.base import base_router
from .routers.users import user_router
from fastapi.staticfiles import StaticFiles
from .config import BASE_DIR

media_dir = BASE_DIR / "media"
os.makedirs(media_dir, exist_ok=True)
app = FastAPI()
app.include_router(user_router, prefix="/users", tags=["users"])
app.include_router(base_router, prefix="/base", tags=["base"])
app.mount("/media", StaticFiles(directory=media_dir), name="media")
