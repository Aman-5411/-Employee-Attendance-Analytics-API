# Employee Attendance & Analytics API

FastAPI + MongoDB service for punching in and out, correcting attendance records, and running attendance analytics. All application code is in `app/main.py`.

## Run

Requires Python 3.11+ and MongoDB 6.0 or newer.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export MONGO_URI="mongodb://localhost:27017"   # a local .env also works
export MONGO_DB="attendance_db"
uvicorn app.main:app --port 8000
```

- `MONGO_URI` and `MONGO_DB` are read from the environment. Real environment variables take priority over `.env`.
- All indexes are created at startup and are idempotent. No manual steps are needed.
- `GET /health` returns 200 once MongoDB answers a ping, otherwise 503.
- Quick local MongoDB: `docker run -p 27017:27017 mongo:7`

## Tests

```bash
pip install pytest
pytest test_helpers.py
```

`test_helpers.py` covers the late, work-hours and overtime rules (R2-R4), including the grace boundary and an overnight shift. The analytics endpoints were not tested against anything larger than the nine sample documents.

## Endpoints

| Method | Path |
|---|---|
| GET | `/health` |
| POST, GET | `/employees` |
| POST | `/attendance/punch-in` |
| POST | `/attendance/punch-out` |
| PATCH | `/attendance/{emp_code}/{date}` |
| GET | `/attendance` |
| GET | `/analytics/employees/{emp_code}/monthly` |
| GET | `/analytics/departments/summary` |
| GET | `/analytics/leaderboard/late` |
| GET | `/analytics/departments/{department}/trend` |
| GET | `/admin/explain/{endpoint}` |

All endpoints from the contract in `openapi.yaml` are implemented.

## Design notes

- **Time:** instants are stored as UTC BSON dates and exchanged as epoch milliseconds. Dates and shift times are IST strings. The client is `tz_aware=True`, and instants are truncated to whole seconds at the boundary (R1).
- **Concurrency:** one punch-in per employee and day is enforced by a unique index. Punch-out is a conditional update. Corrections are guarded on the state that was read, and the loser gets 409.
- **Analytics** are MongoDB aggregation pipelines (`$lookup`, `$setWindowFields`, `$densify`, `$unionWith`) over the stored derived values. Nothing is recomputed from punch times.
- Reasoning behind the indexes and other choices is in `DECISIONS.md`. Defects found in the starter are in `REVIEW.md`.

## Known limitations

<!-- TODO: delete or update this section once the items below are fixed. -->

- PATCH on a seeded record that has no `history` field is rejected with 409. The concurrency guard compares `history` to `[]`, which does not match a missing field.
- `"status": null` in a PATCH body is accepted instead of being rejected with 422.
- `attendance_pct` is returned with 4 decimals. R8 asks for 2 decimals for reported numbers.
- In the department trend, `attendance_rate` and `moving_avg_7d` are rounded with MongoDB's `$round`, which rounds half to even. The contract asks for half-up.
- `/admin/explain` builds simplified pipelines for `employee_monthly`, `department_summary`, `late_leaderboard` and `department_trend`. They are not identical to the real endpoints' pipelines. `department_summary` without a `department` filter scans `employees`, because there is no `joined_on` index.
- `/admin/explain` returns the raw explain document. If it contains BSON types that FastAPI cannot encode (for example `$clusterTime` on a replica set), the response will be a 500.
- `ix_attendance_emp_date_desc` duplicates the unique `(emp_code, date)` index and should be removed.
