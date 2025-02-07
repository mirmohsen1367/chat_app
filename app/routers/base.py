from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_session
from app.helpers.filter import CityFilter, ProvinceFilter
from app.helpers.permissions import is_admin
from app.models.base import City, Province
from app.schemas.base import (
    CityCreate,
    CityResponse,
    CityUpdate,
    PaginatedCityResponse,
    PaginatedProvinceResponse,
    ProvinceCreate,
    ProvinceResponse,
    ProvinceUpdate,
)

base_router = APIRouter()


@base_router.get(
    "/province/",
    response_model=PaginatedProvinceResponse,
)
def province_list(
    skip: int = Query(
        0,
        description="Number of records to skip (offset)",
    ),
    limit: int = Query(
        10,
        description="Number of records to return per page",
    ),
    _=Depends(is_admin),
    name: Optional[str] = None,
    db: Session = Depends(get_session),
):
    query = ProvinceFilter(db).filter(name=name)
    total = query.count()
    provinces = query.offset(skip).limit(limit).all()
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "provinces": provinces,
    }


@base_router.get(
    "/province/{province_id}/",
    response_model=ProvinceResponse,
)
def province_detail(
    province_id: int,
    is_admin=Depends(is_admin),
    db: Session = Depends(get_session),
):
    province = db.query(Province).filter(Province.id == province_id).first()
    if not province:
        raise HTTPException(
            status_code=404,
            detail="Province not found",
        )
    return province


@base_router.post("/province/")
def province_create(
    request: ProvinceCreate,
    is_admin=Depends(is_admin),
    db: Session = Depends(get_session),
):
    existing_province = db.query(Province).filter(Province.name == request.name).first()
    if existing_province:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Province already exists.",
        )
    new_province = Province(name=request.name)
    db.add(new_province)
    db.commit()
    return {"message": "province created successfully."}


@base_router.patch("/province/{province_id}/")
def province_update(
    province_id: int,
    province_update: ProvinceUpdate,
    is_admin=Depends(is_admin),
    db: Session = Depends(get_session),
):
    db_province = db.query(Province).filter(Province.id == province_id).first()
    if not db_province:
        raise HTTPException(
            status_code=404,
            detail="Province not found",
        )

    if province_update.name:
        existing_province = (
            db.query(Province)
            .filter(Province.name == province_update.name, Province.id != province_id)
            .first()
        )
        if existing_province:
            raise HTTPException(
                status_code=400, detail="Province with this name already exist."
            )

    for field, value in province_update.dict(exclude_unset=True).items():
        setattr(db_province, field, value)

    db.commit()
    return {"message": "province updated successfully."}


@base_router.delete("/province/{province_id}/")
def province_delete(
    province_id: int,
    _=Depends(is_admin),
    db: Session = Depends(get_session),
):
    db_province = db.query(Province).filter(Province.id == province_id).first()
    if not db_province:
        raise HTTPException(
            status_code=404,
            detail="Province not found",
        )

    if db_province.cities:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete province because it has associated cities",
        )
    db.delete(db_province)
    db.commit()
    return {"message": "province deleted successfully"}


@base_router.post("/city/")
def city_create(
    request: CityCreate,
    _=Depends(is_admin),
    db: Session = Depends(get_session),
):
    db_province = db.query(Province).filter(Province.id == request.province_id).first()
    if not db_province:
        raise HTTPException(
            status_code=404,
            detail="Province not found",
        )
    city_exists = (
        db.query(City)
        .filter(
            City.province_id == db_province.id,
            City.name == request.name,
        )
        .first()
    )
    if city_exists:
        raise HTTPException(
            status_code=400,
            detail="City with this name and province_id already exists!",
        )
    new_city = City(
        name=request.name,
        province_id=db_province.id,
    )
    db.add(new_city)
    db.commit()
    return {"message": "city created successfully."}


@base_router.patch("/city/{city_id}/")
def city_update(
    city_update: CityUpdate,
    city_id: int,
    _=Depends(is_admin),
    db: Session = Depends(get_session),
):
    db_city = db.query(City).filter(City.id == city_id).first()
    if not db_city:
        raise HTTPException(
            status_code=404,
            detail="City not found",
        )
    for (
        field,
        value,
    ) in city_update.dict(exclude_unset=True).items():
        setattr(
            db_city,
            field,
            value,
        )
    db.commit()
    return {"message": "city updated successfully."}


@base_router.get(
    "/city/{city_id}/",
    response_model=CityResponse,
)
def city_detail(
    city_id: int,
    _=Depends(is_admin),
    db: Session = Depends(get_session),
):
    city = (
        db.query(City)
        .options(joinedload(City.province))
        .filter(City.id == city_id)
        .first()
    )
    if not city:
        raise HTTPException(
            status_code=404,
            detail="City not found",
        )
    return city


@base_router.delete("/city/{city_id}/")
def city_delete(
    city_id: int,
    _=Depends(is_admin),
    db: Session = Depends(get_session),
):
    city = db.query(City).option().filter(City.id == city_id).first()
    if not city:
        raise HTTPException(
            status_code=404,
            detail="City not found",
        )
    db.delete(city)
    db.commit()
    return {"message": "city deleted successfully."}


@base_router.get(
    "/city/",
    response_model=PaginatedCityResponse,
)
def city_list(
    skip: int = Query(
        0,
        description="Number of records to skip (offset)",
    ),
    limit: int = Query(
        10,
        description="Number of records to return per page",
    ),
    name: Optional[str] = None,
    province_id: Optional[int] = None,
    _=Depends(is_admin),
    db: Session = Depends(get_session),
):
    query = CityFilter(db).filter(
        name=name,
        province_id=province_id,
    )
    totlal = query.count()
    cities = query.offset(skip).limit(limit).all()
    return {
        "total": totlal,
        "skip": skip,
        "limit": limit,
        "cities": cities,
    }
