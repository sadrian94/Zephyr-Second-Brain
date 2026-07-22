# Zephyr Second Brain v0.2 — Refactor Plan

**Status:** In progress  
**Theme:** Manual-first, agent-assisted, deterministic core

The v0.2 release separates active work from durable knowledge, keeps core operations local and auditable, and removes direct API behavior from the core. The intended loop is:

```text
Capture freely → request an agent proposal → approve the commitment → apply with deterministic commands → index and review
```

The release introduces `Active/` and root `Archive/`; adds YAML/schema validation, safe lifecycle moves, status reporting, local-only watching, an agent-neutral protocol, and migration support. It explicitly excludes automatic project activation, automatic archiving, watcher-triggered agents, API-key storage, direct LLM calls, and cloud fallback.

See [the protocol](../System/PROTOCOL.md), [capability matrix](capabilities.md), and [migration guide](migration-v0.2.md) for the operational details and current implementation status.
