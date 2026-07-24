# Zephyr v0.3.1 Capability Matrix

| Capability | Status | Boundary |
| --- | --- | --- |
| Five-root layout, YAML validation, index, health report | **Implemented** | Local and deterministic. |
| Approved activation and archiving | **Implemented** | Requires `--approve`; supports `--dry-run`. |
| Link reporting and explicit case-only repairs | **Implemented** | Indexing does not edit links. |
| Local refresh automation | **Implemented** | Validate + index + link report + review queue; System writes only. |
| Review queue | **Implemented** | Deterministic attention signals; never authorizes a note change. |
| Capture triage and source distillation | **Direct or opt-in draft** | Direct request may create one separate Capture draft; scheduled agents require opt-in. |
| Durable-note promotion | **Implemented** | Requires `promote --approve`; supports `--dry-run`. |
| Agent coordination | **Implemented** | One active writer per task/session; optional reviewers and specialists are read-only by default. |
| Review | **Schedulable observe** | One evidence-backed review brief; no note or external-service mutation. |
| External delivery and agent scheduling | **User integration** | Disabled by default and configured outside Zephyr core. |

## Privacy

Zephyr core does not send note contents to an LLM API, store an API key, or use cloud fallback. Invoking an external agent is a separate, user-controlled action. Review that agent’s own privacy and credential settings before giving it vault access.
