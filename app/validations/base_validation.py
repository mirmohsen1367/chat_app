from fastapi import HTTPException
from ..interface.base_validation_interface import BaseValidationInterface
from ..models.base import City, Province


class BaseValidation(BaseValidationInterface):
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
