
from datetime import datetime, timedelta, timezone

from app.main import (
    compute_late_minutes,
    compute_work_hours,
    compute_overtime,
)

IST = timezone(timedelta(hours=5, minutes=30))


def test_late_minutes():
    assert compute_late_minutes(
        datetime(2026, 7, 6, 9, 40, 0, tzinfo=IST), "09:30"
    ) == 0

    assert compute_late_minutes(
        datetime(2026, 7, 6, 9, 40, 1, tzinfo=IST), "09:30"
    ) == 10

    assert compute_late_minutes(
        datetime(2026, 7, 6, 10, 15, 59, tzinfo=IST), "09:30"
    ) == 45


def test_work_hours():
    start = datetime(2026, 7, 6, 9, 30, tzinfo=IST)
    end = datetime(2026, 7, 6, 18, 30, tzinfo=IST)

    assert compute_work_hours(start, end) == 9.0


def test_overtime():
    assert compute_overtime(
        datetime(2026, 7, 6, 18, 59, tzinfo=IST),
        "18:30", "2026-07-06", "09:30"
    ) == 0

    assert compute_overtime(
        datetime(2026, 7, 6, 19, 0, tzinfo=IST),
        "18:30", "2026-07-06", "09:30"
    ) == 30

    assert compute_overtime(
        datetime(2026, 7, 7, 6, 40, tzinfo=IST),
        "06:00", "2026-07-06", "22:00"
    ) == 40
