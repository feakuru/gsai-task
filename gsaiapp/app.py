import datetime
import itertools

import pandas as pd
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .db import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/records/", response_model=schemas.MultipleRecords)
def create_or_update_records(records: schemas.MultipleRecords, db: Session = Depends(get_db)):
    try:
        crud.create_or_update_record(db, records.records)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=e.args[0])
    return records


@app.get("/report/", response_class=Response)
def get_report(company_ids: list[int], db: Session = Depends(get_db)):
    companies = crud.get_companies(db, company_ids)
    non_empty_wks = crud.get_non_empty_wks(db)
    rows = []
    for company in companies:
        for transport_type in ['N', 'D', 'R']:
            rows.append([
                company.name,
                transport_type,
                *[crud.get_median_rate(
                    db=db,
                    company_id=company.id,
                    transport_type=transport_type,
                    wk=wk,
                ) for wk in non_empty_wks],
            ])
    report_frame = pd.DataFrame(rows, columns=["company", "transport type", *non_empty_wks])
    return Response(
        media_type="application/vnd.apache.parquet",
        content=report_frame.to_parquet(),
        headers={
            "Content-Disposition": (
                "attachment; filename=\"report-"
                f"{",".join(str(cid) for cid in company_ids)}"
                f"-{datetime.datetime.now().isoformat(timespec="seconds")}.prq\""
            ),
        },
    )
