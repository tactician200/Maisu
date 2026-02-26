.PHONY: smoke smoke-onboarding qa-gate release-gate qa-release

smoke:
	./scripts/smoke.sh

smoke-onboarding:
	SMOKE_ONBOARDING=1 ./scripts/smoke.sh

# Default release gate workflow (implementation -> QA release)
qa-gate:
	./scripts/qa-gate.sh

# Operator-friendly aliases
release-gate: qa-gate
qa-release: qa-gate
