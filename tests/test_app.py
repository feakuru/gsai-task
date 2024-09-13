import datetime
import logging
import os
import random
import time
from statistics import mean, median

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from gsaiapp.app import app

client = TestClient(app)
logger = logging.getLogger(__name__)

@pytest.fixture(autouse=True)
def clean_database():
    yield
    # delete the test database after running the test
    if os.path.isfile('./gsai_records.db'):
        logger.info("Test teardown: cleaning SQLite database")
        os.remove('./gsai_records.db')

@pytest.fixture(autouse=True)
def fill_companies_from_test_prq_file() -> list[int]:
    prq_data = pd.read_parquet("tests/data/meta.prq")
    prq_data["name"] = prq_data.pop("companyName")
    data = prq_data.to_dict("records")
    for idx, row in enumerate(data):
        jointgs = []
        for key in row:
            if key.startswith("jointgs"):
                jointgs.append(int(key.removeprefix("jointgs")))
        data[idx] = {
            "name": data[idx]["name"],
            "jointgs": jointgs,
        }
    logger.info("Test setup: company creation request: %s...", data[:5])
    create_companies_response = client.post("companies/", json={"companies": data})
    logger.info(
        "Test setup: company creation response: %s, %s...",
        create_companies_response.status_code,
        create_companies_response.content.decode()[:1000],
    )
    return [c["id"] for c in create_companies_response.json()["companies"]]

@pytest.fixture(autouse=True)
def fill_records_from_test_prq_file():
    prq_data = pd.read_parquet("tests/data/data.prq")
    prq_data.total_linehaul_cost = prq_data.total_linehaul_cost.astype(float)
    prq_data.exchange_rate = prq_data.total_linehaul_cost.astype(float)
    prq_data.created_date = prq_data.created_date.map(lambda x: datetime.datetime.strftime(x, '%Y-%m-%dT%H:%M:%SZ'))
    prq_data.last_updated_date = prq_data.last_updated_date.map(lambda x: datetime.datetime.strftime(x, '%Y-%m-%dT%H:%M:%SZ'))
    prq_data.pickup_date = prq_data.pickup_date.map(lambda x: datetime.datetime.strftime(x, '%Y-%m-%dT%H:%M:%SZ'))
    prq_data["company_name"] = prq_data.pop("companyName")
    data = prq_data.to_dict("records")
    logger.info(f"Test setup: record creation request: {data[:5]}, ...")
    create_record_response = client.post("records/", json={"records": data})
    logger.info(f"Test setup: record creation response: {create_record_response.status_code}, {create_record_response.content.decode()[:1000]}...")

def test_read_main(fill_companies_from_test_prq_file: list[int]):
    single_company_times = []
    # checking only 20 random companies because it's convenient when you run tests a lot
    for cid in random.sample(fill_companies_from_test_prq_file, 20):
        req_start = time.time()
        response = client.get(f"/report/?company_ids={cid}")
        req_end = time.time()
        single_company_times.append(req_end - req_start)
        assert response.status_code == 200, response.content.decode()

    logger.info(
        "Single company report statistics: min %.2f, max %.2f, mean %.2f, median %.2f",
        min(single_company_times), max(single_company_times),
        mean(single_company_times), median(single_company_times),
    )

    multiple_companies_times = []
    for _ in range(20):
        cid_str = ",".join(str(cid) for cid in random.sample(fill_companies_from_test_prq_file, 5))
        req_start = time.time()
        response = client.get(f"/report/?company_ids={cid_str}")
        req_end = time.time()
        multiple_companies_times.append(req_end - req_start)
        assert response.status_code == 200, response.content.decode()

    logger.info(
        "Multiple company report statistics: min %.2f, max %.2f, mean %.2f, median %.2f",
        min(multiple_companies_times), max(multiple_companies_times),
        mean(multiple_companies_times), median(multiple_companies_times),
    )
