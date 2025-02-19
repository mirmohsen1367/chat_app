from sqlalchemy import ForeignKey, String, UniqueConstraint, Column, Integer
from app.database import Base
from sqlalchemy.orm import relationship


class Province(Base):
    __tablename__ = "province"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), index=True, unique=True)
    cities = relationship("City", back_populates="province", cascade="all, delete")
    profiles = relationship("Profile", back_populates="province", cascade="all, delete")


class City(Base):
    __tablename__ = "city"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), index=True)
    province_id = Column(Integer, ForeignKey("province.id", ondelete="CASCADE"))
    province = relationship("Province", back_populates="cities")
    __table_args__ = (
        UniqueConstraint("name", "province_id", name="_name_province_id"),
    )
    profiles = relationship("Profile", back_populates="city")
