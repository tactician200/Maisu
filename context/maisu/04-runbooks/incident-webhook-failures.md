# Runbook — Incident: Webhook Failures

## Trigger
- Sudden spike in webhook errors/timeouts
- No responses generated from incoming messages

## Triage (first 10 minutes)
1. Confirm webhook endpoint is reachable.
2. Check n8n execution logs for failing node.
3. Identify scope: all traffic or specific channel/path.
4. Classify severity:
   - Sev1: total outage
   - Sev2: partial degradation

## Stabilization
- If recent deploy/migration happened, roll back that change first.
- Disable non-critical branches in workflow to reduce load.
- Use fallback response path if retrieval/LLM backend is degraded.

## Root Cause Checklist
- Expired API key/credential
- URL/path changed
- Database latency/error spike
- Third-party LLM outage

## Exit Criteria
- Success rate back to baseline
- Last 20 requests processed without critical errors
- Incident note written in checkpoint/decision log
