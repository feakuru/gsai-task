# Python engineer task

Todo:
1. Postgres DB structure
    - company model. id and name
    - jointgs membership model. jointgs id and company id
    - record model. keys: [id', 'miles', 'total_linehaul_cost', 'transport_type', 'created_date', 'last_updated_date', 'currency', 'exchange_rate', 'pickup_date', 'companyName'] + ['wk']

2. Endpoints
    - POST /records: save (if no id) or update (if id) records and also specifically add the week number to them
    - GET /report?company_ids=1,2,3: get report files for specified companies. A report file is aggregated by wk (year-week), transport type and company id, the values are medians of CPM (`total_cost_linehaul` / `miles`)
