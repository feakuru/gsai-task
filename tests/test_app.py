import datetime
import logging
import os

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from gsaiapp.app import app

client = TestClient(app)
logger = logging.getLogger(__name__)

@pytest.fixture(autouse=True)
def clean_database():
    # delete the test database before...
    if os.path.isfile('./gsai_records.db'):
        logger.info("Test setup: cleaning SQLite database")
        os.remove('./gsai_records.db')
    yield
    # ..and after running the test
    if os.path.isfile('./gsai_records.db'):
        logger.info("Test teardown: cleaning SQLite database")
        os.remove('./gsai_records.db')

@pytest.fixture(autouse=True)
def fill_from_test_prq_file():
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

def test_read_main():
    response = client.get("/report")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}
