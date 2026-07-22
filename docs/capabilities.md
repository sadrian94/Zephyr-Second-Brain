# Zephyr v0.2 Capability Matrix

| Capability | Status | Boundary |
| --- | --- | --- |
| Five-root layout, YAML validation, index, health report | **Implemented** | Local and deterministic. |
| Approved activation and archiving | **Implemented** | Requires `--approve`; supports `--dry-run`. |
| Link reporting and explicit case-only repairs | **Implemented** | Indexing does not edit links. |
| Local watcher | **Implemented** | Debounce + index/report only; no agent or network calls. |
| Capture triage, idea expansion, Dream Mode, Slow Mode | **Agent procedure** | An agent may prepare proposals under the protocol; no scheduler or core automation runs them. |
| Bulk guided migration, more schemas, weekly review drafts | **Planned** | Not promised as current behavior. |

## Privacy

Zephyr core does not send note contents to an LLM API, store an API key, or use cloud fallback. Invoking an external agent is a separate, user-controlled action. Review that agent’s own privacy and credential settings before giving it vault access.
