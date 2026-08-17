# releaseforge-app

Demo application used to exercise a full GitOps + progressive delivery
pipeline (CI → Argo CD → Argo Rollouts → Prometheus-gated canary →
automatic rollback).

This app is intentionally simple — it exists to be deployed, not to be
interesting on its own.

## Endpoints

| Endpoint | Purpose |
|---|---|
| `GET /` | Returns version, hostname, environment, request count |
| `GET /version` | Returns just the version string |
| `GET /health` | Liveness/readiness probe target |
| `GET /payment` | Simulated endpoint; can be made to fail via `SIMULATE_FAILURE=true` for canary-rollback demos |

## Local development

\`\`\`bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
\`\`\`

## Tests

\`\`\`bash
python -m pytest tests/ -v
\`\`\`

## Docker

\`\`\`bash
docker build -t releaseforge-app:v1.0 .
docker run -p 8000:8000 -e APP_VERSION=v1.0 releaseforge-app:v1.0
\`\`\`

## Environment variables

| Var | Default | Purpose |
|---|---|---|
| `APP_VERSION` | `v1.0` | Injected at build/deploy time to distinguish versions |
| `APP_ENV` | `local` | Environment label |
| `SIMULATE_FAILURE` | `false` | When `true`, `/payment` randomly returns 500s — used to test automatic rollback |