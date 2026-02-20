# Quality Guardrail Monitoring

Lightweight artifacts for ops monitoring of provider fallbacks and boilerplate guardrails.

## Log Event Examples

Use JSON log lines where possible so they are easy to grep/jq. Field names are illustrative; adjust to your logger.

Provider success (no fallback):

```json
{"ts":"2026-02-20T02:31:14Z","level":"INFO","msg":"rag.query.success","route":"/rag/query","provider":"openai","fallback_used":false,"latency_ms":842,"request_id":"req_2f9b"}
```

Provider fallback (used):

```json
{"ts":"2026-02-20T02:31:48Z","level":"WARN","msg":"rag.query.fallback","route":"/rag/query","provider":"fallback","fallback_used":true,"fallback_reason":"ProviderError","latency_ms":912,"request_id":"req_30ac"}
```

Boilerplate guardrail signal (if emitted by the checker):

```json
{"ts":"2026-02-20T02:32:07Z","level":"WARN","msg":"quality.guardrail.triggered","route":"/rag/query","provider":"openai","fallback_used":false,"guardrail_reason":"low_value_boilerplate","request_id":"req_317a"}
```

## Grep/JQ Snippets

Find all fallback events in a log file:

```bash
rg 'fallback_used":true' /var/log/maisu/api.log
```

Count fallback events by reason (JSON lines):

```bash
jq -r 'select(.fallback_used==true) | .fallback_reason // "unknown"' /var/log/maisu/api.log | sort | uniq -c | sort -nr
```

Show recent fallback events with key fields:

```bash
jq -r 'select(.fallback_used==true) | "[\(.ts)] \(.route) provider=\(.provider) reason=\(.fallback_reason // "unknown") request_id=\(.request_id // "-")"' /var/log/maisu/api.log | tail -n 20
```

Surface boilerplate guardrail triggers (if logged):

```bash
rg 'quality.guardrail.triggered' /var/log/maisu/api.log
```

## Scripted Summary

Use the repo script to summarize fallback reasons and recent examples from JSON logs:

```bash
scripts/quality-guardrail-report.sh /var/log/maisu/api.log
```

Pipe from another command:

```bash
rg -N 'rag.query' /var/log/maisu/api.log | scripts/quality-guardrail-report.sh
```

Output includes totals, counts by reason/provider/route, and recent examples.
