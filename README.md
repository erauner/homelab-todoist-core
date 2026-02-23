# homelab-todoist-core

Shared Todoist domain helpers and deterministic policy evaluation for:

- `homelab-autodoist-events`
- `homelab-todoist-cli`
- cron-driven OpenClaw orchestration

## Scope

This library is side-effect free by design. It does not call Todoist/OpenClaw APIs directly.

It provides:

- normalized task models
- due/time parsing helpers
- candidate selection/ranking
- policy decisions (`should_notify`, `mode`, `reason`)
- OpenClaw payload builders

## Install

```bash
uv add homelab-todoist-core --index https://nexus.erauner.dev/repository/pypi-hosted/simple
```

## Local development

```bash
uv sync --extra dev
uv run pytest -q
uv run ruff check src/ tests/
```
