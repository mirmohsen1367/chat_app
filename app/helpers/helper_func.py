from fastapi.exceptions import HTTPException
from passlib.context import CryptContext
import uuid
from ..config import BASE_DIR
from pathlib import Path
import shutil


def get_or_404(db, model, id):
    obj = db.query(model).filter(model.id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail=f"{model.__name__} not found")
    return obj


password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_hashed_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(password: str, hashed_pass: str) -> bool:
    return password_context.verify(password, hashed_pass)


def create_image_media(folder_name, image):
    object_folder = BASE_DIR / "media" / f"{folder_name}"
    object_folder.mkdir(parents=True, exist_ok=True)
    unique_filename = f"{uuid.uuid4()}{Path(image.filename).suffix}"
    file_location = object_folder / unique_filename
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
