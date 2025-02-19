from sqlalchemy import String, Column, Integer, ForeignKey, Boolean, DateTime, func
from app.database import Base
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), index=True, unique=True)
    phone_number = Column(String(11), index=True, unique=True)
    password = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    is_staff = Column(Boolean, default=False)
    created = Column(DateTime, default=func.now())
    updated = Column(DateTime, default=func.now(), onupdate=func.now())
    profile = relationship("Profile", back_populates="user", uselist=False)


class Profile(Base):
    __tablename__ = "profile"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    image = Column(String(255), nullable=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), unique=True)
    user = relationship("User", back_populates="profile")
    city_id = Column(Integer, ForeignKey("city.id", ondelete="CASCADE"))
    city = relationship("City", back_populates="profiles")
    province_id = Column(Integer, ForeignKey("province.id", ondelete="CASCADE"))
    province = relationship("Province", back_populates="profiles")
