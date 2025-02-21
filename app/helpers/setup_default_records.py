from app.database import SessionLocal
from app.helpers.helper_func import get_hashed_password
from app.helpers.validators import validate_phone_number, validate_is_strong
from app.models.users import User, Profile
from app.models.base import City, Province
from contextlib import contextmanager


@contextmanager
def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def get_or_create_province(db, value):
    if province := db.query(Province).filter(Province.name == value).first():
        return province
    province = Province(name=value)
    db.add(province)
    db.commit()
    return province


def get_or_create_city(db, province, value):
    if (
        city := db.query(City)
        .filter(City.name == value, City.province_id == province.id)
        .first()
    ):
        return city
    city = City(name=value, province=province)
    db.add(city)
    db.commit()
    return city


def create_admin_user():
    with get_session() as session:
        username = input("please enter username: ")
        if not username:
            raise ValueError("please enter valid username")
        if session.query(User).filter(username == username).first() is not None:
            raise ValueError("user with username already exists!")
        phone_number = input("please enter phone number: ")
        validate_phone_number(phone_number)
        if session.query(User).filter(phone_number == phone_number).first() is not None:
            raise ValueError("user with username already exists!")
        password = input("please enter password: ")
        validate_is_strong(password)
        password_hash = get_hashed_password(password)
        province = get_or_create_province(session, value="تهران")
        city = get_or_create_city(session, province, value="تهران")
        user = User(
            username=username,
            phone_number=phone_number,
            is_staff=True,
            password=password_hash,
        )
        profile = Profile(city=city, province=province, user=user)
        session.add_all([user, profile])
        session.commit()


if __name__ == "__main__":
    create_admin_user()
