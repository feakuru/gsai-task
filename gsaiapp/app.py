import datetime

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

# this endpoint is only used for ease of testing - it would not be present in a production env
@app.post("/companies/", response_model=schemas.Companies)
def create_companies(companies: schemas.Companies, db: Session = Depends(get_db)):
    try:
        result = crud.create_companies(db, companies.companies)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=e.args[0])
    return schemas.Companies(companies=result)

@app.post("/records/", response_model=schemas.MultipleRecords)
def create_or_update_records(records: schemas.MultipleRecords, db: Session = Depends(get_db)):
    try:
        crud.create_or_update_record(db, records.records)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=e.args[0])
    return records


@app.get("/report/", response_class=Response)
def get_report(company_ids: str, db: Session = Depends(get_db)):
    companies = crud.get_companies(db, [int(cid) for cid in company_ids.split(',')])
    non_empty_wks = crud.get_non_empty_wks(db)
    rows = []

    # this cycle is the main performance bottleneck for this application. as mentioned in
    # `crud.py:get_median_rate`, it could be avoided and wrapped into one SQL request.
    # even without this optimization, the current execution times are mostly below
    # 2s for one company and 7s for 5 companies on my machine with the test data,
    # which I consider to be a good result for an MVP.
    for company in companies:
        for transport_type in ['N', 'D', 'R']:
            row_data = [
                company.name,
                transport_type,
                *[crud.get_median_rate(
                    db=db,
                    company_id=company.id,
                    transport_type=transport_type,
                    wk=wk,
                ) for wk in non_empty_wks],
            ]
            rows.append(row_data)
    report_frame = pd.DataFrame(rows, columns=["company", "transport type", *non_empty_wks])
    return Response(
        media_type="application/vnd.apache.parquet",
        content=report_frame.to_parquet(),
        headers={
            "Content-Disposition": (
                "attachment; filename=\"report-"
                f"{",".join(str(cid) for cid in company_ids or [])}"
                f"-{datetime.datetime.now().isoformat(timespec="seconds")}.prq\""
            ),
        },
    )
