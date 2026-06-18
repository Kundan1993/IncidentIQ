# Application Incident Runbook

## Spike in 5xx errors
Symptoms: elevated 500/503 rate, error budget burning.
1. Check which endpoint is erroring in the logs / traces.
2. Correlate with the most recent deployment.
3. If it started right after a deploy, roll back first, debug later.
4. Restart the affected service if it's in a bad state.

## Memory leak
Symptoms: memory climbs steadily until OOM, periodic restarts.
1. Capture a heap profile from one instance.
2. Restart the service to restore capacity while investigating.
3. Ship the fix and monitor the memory curve.

## Rate limit / throttling
1. Check upstream rate-limit headers and current QPS.
2. Add caching or back off retries; request a higher quota if legit.
