# Runbook — n8n Workflow Restore/Import

## Purpose
Restore MVP workflows quickly after environment reset or accidental deletion.

## Inputs
- Exported workflow JSON files
- Environment variables present (`N8N_WEBHOOK_URL`, API keys)

## Steps
1. Open n8n UI and select target environment.
2. Import workflow JSON.
3. Re-map credentials (LLM, DB, webhooks).
4. Verify webhook URLs and test endpoints.
5. Run one smoke execution per critical flow:
   - inbound message
   - retrieval call
   - response generation
6. Activate workflow only after smoke success.

## Validation Signals
- Workflow active and green in n8n
- No missing credential warnings
- Test execution writes expected logs/output

## Common Failure Modes
- Missing credentials after import
- Changed webhook path/URL
- DB function mismatch vs expected schema

## Rollback
- Deactivate imported workflow
- Re-enable previous known-good workflow version
