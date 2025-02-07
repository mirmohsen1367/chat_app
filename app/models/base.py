from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Province(Base):
    __tablename__ = "province"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    cities: Mapped[list["City"]] = relationship(back_populates="province")


class City(Base):
    __tablename__ = "city"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    province_id: Mapped[int] = mapped_column(
        ForeignKey("province.id", ondelete="CASCADE")
    )
    province: Mapped[Province] = relationship(back_populates="cities")
    __table_args__ = (
        UniqueConstraint("name", "province_id", name="_name_province_id"),
    )
