from sqlalchemy.orm import Session, joinedload

from app.models.base import City, Province


class ProvinceFilter:
    def __init__(self, db: Session):
        self.db = db

    def filter(self, name: str):
        query = self.db.query(Province)
        if name:
            query = query.filter(Province.name.ilike(f"%{name}%"))
        return query


class CityFilter:
    def __init__(self, db: Session):
        self.db = db

    def filter(self, name: str | None = None, province_id: int | None = None):
        query = self.db.query(City).options(joinedload(City.province))
        if name:
            query = query.filter(City.name.ilike(f"%{name}%"))
        if province_id:
            query = query.filter(City.province_id == province_id)
        return query
