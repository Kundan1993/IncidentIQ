# Infrastructure / Kubernetes Runbook

## OOMKilled pods
Symptoms: pods restarting, `reason: OOMKilled`, memory limit hit.
1. `kubectl describe pod <pod>` and check Last State.
2. Compare actual usage vs the memory limit.
3. Raise the memory limit or fix the leak, then redeploy.
4. As a stop-gap, scale out replicas to spread load.

## Disk full
Symptoms: "no space left on device", failing writes.
1. Identify the largest directories on the node.
2. Rotate / ship logs, clear old container images.
3. Expand the volume (PVC resize) if usage is legitimate.

## Node not ready
1. Check kubelet status and node conditions.
2. Cordon and drain the node, let the scheduler reschedule pods.
3. Replace the node if hardware-related.
