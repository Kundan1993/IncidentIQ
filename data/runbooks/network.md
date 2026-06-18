# Network Incident Runbook

## DNS resolution failures
Symptoms: "could not resolve host", intermittent timeouts to internal services.
1. Test resolution from inside a pod: `nslookup <service>`.
2. Check CoreDNS pods are healthy and not throttled.
3. Restart CoreDNS if it's wedged; verify upstream resolvers.

## TLS / certificate expiry
Symptoms: "certificate has expired", handshake failures.
1. Check the cert expiry: `openssl s_client -connect host:443`.
2. Renew / rotate the certificate and reload the ingress.
3. Add an expiry alert at 30 days if missing.

## High latency / packet loss
1. Check load balancer health and recent deploys.
2. Roll back the last deployment if latency started right after a release.
