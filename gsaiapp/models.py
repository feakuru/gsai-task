import datetime
import enum

from sqlalchemy import (Column, DateTime, Enum, Float, ForeignKey, Integer,
                        String, Table)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class TransportTypeEnum(enum.Enum):
    N = 0
    D = 1
    R = 2

class CurrencyEnum(enum.Enum):
    USD = 0
    EUR = 1
    CAD = 2

association_table = Table(
    "association_table",
    Base.metadata,
    Column("jointg_id", ForeignKey("jointgs.id"), primary_key=True),
    Column("company_id", ForeignKey("companies.id"), primary_key=True),
)

class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    records: Mapped[list["Record"]] = relationship(back_populates="company")
    jointgs: Mapped[list["JointG"]] = relationship(secondary=association_table, back_populates="companies")

class JointG(Base):
    __tablename__ = "jointgs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    companies: Mapped[list["Company"]] = relationship(secondary=association_table, back_populates="jointgs")

class Record(Base):
    __tablename__ = "records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    miles: Mapped[float] = mapped_column(Float)
    total_linehaul_cost: Mapped[float] = mapped_column(Float)
    transport_type: Mapped[str] = mapped_column(Enum(TransportTypeEnum))
    created_date: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=datetime.datetime.now,
    )
    last_updated_date: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        onupdate=datetime.datetime.now,
    )
    currency: Mapped[str] = mapped_column(Enum(CurrencyEnum))
    exchange_rate: Mapped[float] = mapped_column(Float)
    pickup_date: Mapped[datetime.datetime] = mapped_column(DateTime)
    company_id: Mapped[int | None] = mapped_column(ForeignKey("companies.id"))
    company: Mapped["Company"] = relationship(back_populates="records")

    # this is a "private" attribute, in the sense that schemas will never display it.
    # in a Postgres db, it would be an index over extract('week', created_date),
    # but for my simplified SQLite example i just write it manually.
    # values are integers formed like 202403, where 2024 is the year and 03 is the week
    wk: Mapped[int] = mapped_column(Integer)
