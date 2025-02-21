from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

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
from app.helpers.helper_func import get_or_404

base_router = APIRouter()


@base_router.get("/province/", response_model=PaginatedProvinceResponse)
def province_list(
    skip: int = Query(
        0,
        description="Number of records to skip (offset)",
    ),
    limit: int = Query(
        10,
        description="Number of records to return per page",
    ),
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
def province_detail(province_id: int, db: Session = Depends(get_session)):
    province = get_or_404(db, Province, province_id)
    return province


@base_router.post("/province/")
def province_create(
    request: ProvinceCreate,
    _=Depends(is_admin),
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
    return {"message": "Province created successfully."}


@base_router.patch("/province/{province_id}/")
def province_update(
    province_id: int,
    province_update: ProvinceUpdate,
    _=Depends(is_admin),
    db: Session = Depends(get_session),
):
    province = get_or_404(db, Province, province_id)
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
        setattr(province, field, value)

    db.commit()
    return {"message": "Province updated successfully."}


@base_router.delete("/province/{province_id}/")
def province_delete(
    province_id: int,
    _=Depends(is_admin),
    db: Session = Depends(get_session),
):
    province = get_or_404(db, Province, province_id)
    if not province:
        raise HTTPException(
            status_code=404,
            detail="Province not found",
        )

    if province.cities:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete province because it has associated cities",
        )
    if province.profiles:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete province because it has associated profiles",
        )

    db.delete(province)
    db.commit()
    return {"message": "province deleted successfully"}


@base_router.get("/city/", response_model=PaginatedCityResponse)
def city_list(
    skip: int = Query(0, description="Number of records to skip (offset)"),
    limit: int = Query(10, description="Number of records to return per page"),
    name: Optional[str] = None,
    province: Optional[int] = None,
    db: Session = Depends(get_session),
):
    query = CityFilter(db).filter(name=name, province_id=province)
    totlal = query.count()
    cities = query.offset(skip).limit(limit).all()
    return {"total": totlal, "skip": skip, "limit": limit, "cities": cities}


@base_router.get("/city/{city_id}/", response_model=CityResponse)
def city_detail(city_id: int, db: Session = Depends(get_session)):
    city = get_or_404(db, City, city_id)
    if not city:
        raise HTTPException(status_code=404, detail="City not found")
    return city


@base_router.post("/city/")
def city_create(
    request: CityCreate,
    db: Session = Depends(get_session),
    _=Depends(is_admin),
):
    province = get_or_404(db, Province, request.province_id)
    city_exists = (
        db.query(City)
        .filter(City.province_id == province.id, City.name == request.name)
        .first()
    )
    if city_exists:
        raise HTTPException(
            status_code=400,
            detail="City with this name and province_id already exists!",
        )
    new_city = City(name=request.name, province_id=province.id)
    db.add(new_city)
    db.commit()
    return {"message": "City created successfully."}


@base_router.patch("/city/{city_id}/")
def city_update(
    city_update: CityUpdate,
    city_id: int,
    _=Depends(is_admin),
    db: Session = Depends(get_session),
):
    city = get_or_404(db, City, city_id)
    for field, value in city_update.dict(exclude_unset=True).items():
        setattr(city, field, value)
    db.commit()
    return {"message": "City updated successfully."}


@base_router.delete("/city/{city_id}/")
def city_delete(city_id: int, _=Depends(is_admin), db: Session = Depends(get_session)):
    city = get_or_404(db, City, city_id)
    if city.profiles:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete city because it has associated profiles",
        )
    db.delete(city)
    db.commit()
    return {"message": "City deleted successfully."}
