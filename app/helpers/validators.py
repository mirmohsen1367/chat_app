import re
from fastapi import HTTPException

from app.helpers.helper_func import get_hashed_password

from ..models.base import City, Province
from ..models.users import User


class BaseValidation:
    def __init__(self, db):
        self.db = db

    def validate_province(self, value):
        province = self.db.query(Province).filter(Province.id == value).first()
        if province:
            return province
        else:
            raise HTTPException(detail="Province not found", status_code=400)

    def validate_city(self, province_id, value):
        city = (
            self.db.query(City)
            .filter(City.id == value, City.province_id == province_id)
            .first()
        )
        if city:
            return city
        else:
            raise HTTPException(detail="City not found", status_code=400)


class CreateUserValidation:
    def __init__(
        self,
        db,
        username,
        phone_number,
        password,
    ):
        self.db = db
        self.username = username
        self.phone_number = phone_number
        self.password = password

    @staticmethod
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

    @staticmethod
    def validate_phone_number(value: str) -> str:
        if not re.match(r"^09\d{9}$", value):
            raise HTTPException(detail="Invalid phone_number", status_code=400)
        return value

    def validate_phone_number_exists(self, value):
        phone_number = self.validate_phone_number(value=value)
        user = self.db.query(User).filter(User.phone_number == phone_number).first()
        if user is not None:
            raise HTTPException(
                detail="A user with phone_number already exists", status_code=400
            )
        return phone_number

    def validate_username_exists(self, value):
        user = self.db.query(User).filter(User.username == value).first()
        if user is not None:
            raise HTTPException(
                detail="A user with username already exists", status_code=400
            )
        return value

    def validate_input_data(self):
        username = self.validate_username_exists()
        phone_number = self.validate_phone_number_exists()
        password = get_hashed_password(self.validate_is_strong())
        return {
            "username": username,
            "phone_number": phone_number,
            "password": password,
        }


class UpdateUserValidation(CreateUserValidation):
    def __init__(
        self,
        db,
        username=None,
        phone_number=None,
        password=None,
    ):
        super().__init__(
            db, username=username, phone_number=phone_number, password=password
        )

    def validate_input_data(self):
        data = {}
        if self.username:
            username = self.validate_username_exists(self.username)
            data.update({"username": username})
        if self.phone_number:
            phone_number = self.validate_phone_number_exists(self.phone_number)
            data.update({"phone_number": phone_number})
        if self.password:
            password = self.validate_is_strong(self.password)
            data.update({"phone_number": get_hashed_password(password=password)})
        return data


class CreateProfileValidation:
    def __init__(self, db, province, city, image, first_name=None, last_name=None):
        self.db = db
        self.province = province
        self.city = city
        self.image = image
        self.first_name = first_name
        self.last_name = last_name

    @staticmethod
    def validate_image(value: str) -> str:
        image_file_regex = re.compile(r".*\.(jpg|jpeg|png|gif|bmp)$", re.IGNORECASE)
        if not image_file_regex.match(value):
            raise HTTPException(
                status_code=400,
                detail="Invalid image file type. Allowed formats are jpg, jpeg, png, gif, bmp.",
            )
        return value

    def validate_input_data(self):
        base_validation = BaseValidation(self.db)
        province = base_validation.validate_province_id(self.province)
        city = base_validation.validate_city_id(self.city, self.province)
        image = self.validate_image(self.image)
        return {
            "province": province,
            "city": city,
            "image": image,
            "first_name": self.first_name,
            "last_name": self.last_name,
        }


class UpdateProfileValidation(CreateProfileValidation):
    def __init__(
        self, db, province=None, city=None, image=None, first_name=None, last_name=None
    ):
        super().__init__(
            db,
            province=province,
            city=city,
            image=image,
            first_name=first_name,
            last_name=last_name,
        )

    def validate_input_data(self):
        data = {}
        base_validation = BaseValidation(self.db)
        if self.province:
            province = base_validation.validate_province_id(self.province)
            data.update({"province": province})
        if self.city:
            city = base_validation.validate_province_id(self.city, self.province)
            data.update({"city": city})
        if self.image:
            image = self.validate_image(self.image)
            data.update({"image": image})
        if self.first_name:
            data.update({"first_name": self.first_name})
        if self.last_name:
            data.update({"last_name": self.last_name})
        return data
