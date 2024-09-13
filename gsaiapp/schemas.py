import datetime

from pydantic import BaseModel


class Record(BaseModel):
    id: int | None = None
    miles: float
    total_linehaul_cost: float
    transport_type: str
    created_date: datetime.datetime
    last_updated_date: datetime.datetime
    currency: str
    exchange_rate: float
    pickup_date: datetime.datetime
    company_name: str

    class Config:
        from_attributes = True


class MultipleRecords(BaseModel):
    records: list[Record]


class Company(BaseModel):
    id: int | None = None
    name: str
    jointgs: list[int]


class Companies(BaseModel):
    companies: list[Company]
