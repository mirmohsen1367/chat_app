from typing import List
from typing import Optional

from pydantic import BaseModel


class ProvinceResponse(BaseModel):
    id: int
    name: str


class PaginatedProvinceResponse(BaseModel):
    total: int
    skip: int
    limit: int
    provinces: List[ProvinceResponse]


class ProvinceCreate(BaseModel):
    name: str


class ProvinceUpdate(ProvinceCreate):
    pass


class CityBase(BaseModel):
    name: str
    province_id: int


class CityCreate(CityBase):
    pass


class CityUpdate(BaseModel):
    name: Optional[str] = None
    province_id: Optional[str] = None


class CityResponse(BaseModel):
    id: int
    name: str
    province: ProvinceResponse


class CitySchema(BaseModel):
    id: int
    name: str


class PaginatedCityResponse(BaseModel):
    total: int
    skip: int
    limit: int
    cities: List[CityResponse]
