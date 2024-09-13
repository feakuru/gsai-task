# Python engineer task

This application is designed to allow quick PRQ report generation on the company linehauls from
the provided test dataset. Not everything is finished per se, but I have tried to leave comments
in places which would obviously require further work in a real setting.

Some important notes:

0. Please read the code in the following order (while paying special attention to the comments):
    1. `pyproject.toml` (standard project definition in terms of dependencies etc.)
    2. `gsaiapp/db.py` (database boilerplate)
    3. `gsaiapp/models.py` (database ORM models)
    4. `gsaiapp/schemas.py` (schemas for the models' representation in the API)
    5. `gsaiapp/crud.py` (CRUD utilities that provide a separate interface to be used by the app's views)
    6. `gsaiapp/app.py` (main FastAPI app)

    To run the app and test it manually, run `uvicorn gsaiapp.app:app`

1. Postgres DB structure
    - records are stored in a separate table;
    - the relationships between models are simple and allow for various future in-database optimisations;
    - jointgs has been turned into a membership model. this removes the "million `false` values"-style data duplication and allows for selection over `JOIN`ed tables.

2. App endpoints
    - POST /records: save (if no id present) or update (if id present) records and also specifically add the week number to them under the hoow
    - GET /report?company_ids=1,2,3: get report files for specified companies. A report file is aggregated by wk (year-week), transport type and company id, the values are medians of CPM (`total_cost_linehaul` / `miles`).

3. jointgs are currently not supported for selection for report creation, but the tests check the multiple companies case to allow at least an approximate estimation of the performance of a jointg request under the current query structure.

4. Tests: there is currently only one big test, it runs for quite some time, simply checks that nothing is obviously broken and provides some logs to estimate the performance of the app on the test dataset.
