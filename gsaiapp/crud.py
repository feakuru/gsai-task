from statistics import median

from sqlalchemy.orm import Session

from . import models, schemas


def get_median_rate(db: Session, company_id: int, transport_type: str, wk: int) -> float:
    # this query would also be different for the Postgres index case described in ./models.py
    # it would leverage the index, using extract('week') in the select filter.
    # this query would be significantly faster in Postgres, because it supports medians
    # (by way of `PERCENTILE(50%, value)`). this would also allow to select medians for
    # every row right away, with one SQL query.

    # there are ways to manually calculate median from inside SQLite,
    # which would improve the speed in this case, but bring down code readability.

    records = db.query(models.Record).filter(
        models.Record.wk == wk,
        models.Record.company.id == company_id,
        models.Record.transport_type == transport_type,
    ).all()
    return median([record.total_linehaul_cost / record.miles for record in records])


def create_or_update_record(db: Session, records: list[schemas.Record]):
    # this line would benefit from in-memory caching in a real setting
    company_ids = {company.name: company.id for company in get_companies(db)}

    for record in records:
        if record.company_name not in company_ids:
            raise ValueError(f"Company {record.company_name} not found")
        rec_kwargs = record.dict()
        rec_kwargs["company_id"] = company_ids[rec_kwargs.pop("company_name")]
        db_record = models.Record(
            **record.dict(),
            wk=int(record.created_date.isoformat("%Y%W")),
        )
        db.add(db_record)
    db.commit()


def get_companies(db: Session, company_ids: list[int] | None = None) -> list[models.Company]:
    company_query = db.query(models.Company).filter()
    if company_ids:
        company_query = company_query.filter(models.Company.id.in_(company_ids))
    return company_query.all()

def get_non_empty_wks(db: Session) -> list[int]:
    return db.query(models.Record).with_entities(models.Record.wk).distinct().all()
