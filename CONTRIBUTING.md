# Contributing to Specula API

## Setup

```bash
python -m venv .venv
source .venv/bin/activate        # POSIX (macOS/Linux)
.venv\Scripts\activate           # Windows PowerShell
pip install -r requirements.txt
cp .env.example .env
python -m pytest
uvicorn app.main:app --reload
```

## Before opening a PR

- Run `python -m pytest` and make sure it passes.
- Keep the PR scoped to one issue; reference it with `Closes #N`.
- Update README.md if you changed a route's behavior.

## Related repos

- [specula-contracts](https://github.com/Specula-Labs/specula-contracts) — emits the `flagged` events this service reads.
- [specula-frontend](https://github.com/Specula-Labs/specula-frontend) — dashboard consuming this service's screening, network, and event endpoints.
