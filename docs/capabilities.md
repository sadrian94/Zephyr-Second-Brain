# Zephyr v0.3.0 Capability Matrix

| Capability | Status | Boundary |
| --- | --- | --- |
| Five-root layout, YAML validation, index, health report | **Implemented** | Local and deterministic. |
| Approved activation and archiving | **Implemented** | Requires `--approve`; supports `--dry-run`. |
| Link reporting and explicit case-only repairs | **Implemented** | Indexing does not edit links. |
| Local refresh automation | **Implemented** | Validate + index + link report + review queue; System writes only. |
| Review queue | **Implemented** | Deterministic attention signals; never authorizes a note change. |
| Capture triage, idea expansion, source distillation | **Opt-in draft** | External agent may create a separate Capture draft; source remains untouched. |
| Durable-note promotion | **Implemented** | Requires `promote --approve`; supports `--dry-run`. |
| Agent coordination | **Implemented** | One active writer per task/session; optional reviewers and specialists are read-only by default. |
| Dream Mode, weekly review, reminder brief | **Schedulable observe** | Generated report only; no note or external-service mutation. |
| External delivery and agent scheduling | **User integration** | Disabled by default and configured outside Zephyr core. |

## Privacy

Zephyr core does not send note contents to an LLM API, store an API key, or use cloud fallback. Invoking an external agent is a separate, user-controlled action. Review that agent’s own privacy and credential settings before giving it vault access.
