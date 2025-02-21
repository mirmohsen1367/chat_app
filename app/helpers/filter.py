from sqlalchemy.orm import Session

from app.models.base import City, Province
from typing import Optional

from app.models.users import Profile, User
from sqlalchemy.orm import joinedload


class ProvinceFilter:
    def __init__(self, db: Session):
        self.db = db

    def filter(self, name: Optional[str] = None):
        query = self.db.query(Province).order_by(Province.id.desc())
        if name:
            query = query.filter(Province.name.ilike(f"%{name}%"))
        return query


class CityFilter:
    def __init__(self, db: Session):
        self.db = db

    def filter(self, name: Optional[str] = None, province_id: Optional[int] = None):
        query = (
            self.db.query(City)
            .options(joinedload(City.province))
            .order_by(City.id.desc())
        )
        if name:
            query = query.filter(City.name.ilike(f"%{name}%"))
        if province_id:
            query = query.filter(City.province_id == province_id)
        return query


class ProfileFilter:
    def __init__(self, db: Session):
        self.db = db

    def filter(
        self,
        username: Optional[str] = None,
        phone_number: Optional[str] = None,
        province: Optional[int] = None,
        city: Optional[int] = None,
        is_active: Optional[int] = None,
        is_staff: Optional[int] = None,
    ):
        query = (
            self.db.query(Profile)
            .join(User)
            .join(Province)
            .join(City)
            .options(
                joinedload(Profile.user),
                joinedload(Profile.city),
                joinedload(Profile.province),
            )
            .order_by(Profile.id.desc())
        )
        if username:
            query = query.filter(User.username.ilike(f"%{username}%"))
        if phone_number:
            query = query.filter(User.phone_number.ilike(f"%{phone_number}%"))
        if province:
            query = query.filter(Province.id == province)
        if city:
            query = query.filter(City.id == city)
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        if is_staff is not None:
            query = query.filter(User.is_staff == is_staff)

        return query
