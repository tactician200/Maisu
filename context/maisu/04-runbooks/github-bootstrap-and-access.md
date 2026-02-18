# Runbook — GitHub Bootstrap & Access (Maisu)

## Purpose
Ensure repository access is working for contributors/agents and avoid blocked delivery.

## Preconditions
- Git installed
- SSH key configured in GitHub account
- Repo remote expected: `git@github.com:tactician200/Maisu.git`

## Steps
1. Verify remote:
   ```bash
   git remote -v
   ```
2. Verify SSH auth:
   ```bash
   ssh -T git@github.com
   ```
3. Verify push permission (dry run):
   ```bash
   git push --dry-run origin main
   ```
4. If blocked:
   - confirm key in `~/.ssh`
   - add public key in GitHub settings
   - retry step 2/3

## Validation Signals
- `git remote -v` shows correct repo
- SSH auth succeeds
- dry-run push does not fail with permission denied

## Rollback
- No system changes beyond local Git/SSH config.
- Revert remote URL if mistakenly modified:
  ```bash
  git remote set-url origin git@github.com:tactician200/Maisu.git
  ```
