# DECISIONS.md

1. **Indexes.** `employees`: unique `emp_code` (identity, 409 on duplicates, default sort) and `(department, emp_code)` (filter plus sort, headcount lookups). `attendance_logs`: unique `(emp_code, date)` (one record per day, race guard, per-employee queries), `(date desc, emp_code)` (list sort, date-range analytics) and `(status, date desc, emp_code)` (status filter). I rejected `(emp_code, punch_in)` for punch-out: an employee has few records, so an in-memory sort is cheap and the index would slow every write.

2. **Punch-in race.** Both requests compute the same date and call `insert_one`. The unique `(emp_code, date)` index lets one succeed; the other gets `DuplicateKeyError`, which I return as 409. There is no read before the write.

3. **Ties.** The leaderboard uses `$rank`, so tied employees share a rank. `limit` applies to the rank, so every tied row at the cutoff is returned, even if that exceeds `limit` rows. Ties are ordered by `emp_code`.

4. **Headcount.** The summary starts from `employees` (joined on or before month end) and then looks up logs. An employee with no logs gets an empty lookup, is kept by `preserveNullAndEmptyArrays`, and still counts 1.

5. **100x data.** I would keep a monthly summary per employee, updated on punch and correction, instead of aggregating raw logs per request, and use keyset pagination instead of `skip`.
