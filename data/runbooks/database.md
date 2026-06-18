# Database Incident Runbook

## Connection pool exhausted
Symptoms: "FATAL: remaining connection slots are reserved", spike in connection count, app timeouts.
1. Check active connections: `SELECT count(*) FROM pg_stat_activity;`
2. Identify idle-in-transaction sessions and terminate the worst offenders.
3. Restart the application pods to release leaked connections.
4. Raise `max_connections` or add PgBouncer if this recurs.

## Slow queries / high latency
1. Check `pg_stat_statements` for the top queries by total time.
2. Look for missing indexes on the hot query's filter columns.
3. If a single query is locking, consider killing it and adding an index.

## Replication lag
1. Compare primary vs replica LSN.
2. Throttle heavy write batches; scale up the replica if needed.
