# Zephyr v0.3.0: Agency-Preserving Automation

Capture should be easy; commitments should be visible. Zephyr separates the two.

The system accepts unstructured material in `Capture/`, durable knowledge in `Brain/`, explicitly chosen work in `Active/`, and historical records in `Archive/`. A proposal is not a commitment: an agent can offer structure, but the human decides whether it becomes active work or an archive record.

Automation should remove clerical friction, not conceal a decision. Zephyr automatically observes mechanical facts and builds an attention queue. Semantic agents may prepare separate drafts only after opt-in. Commitments, prose changes, and lifecycle moves still require current human approval.

The important mechanisms remain inspectable: Markdown is the record, YAML is parsed with a standard parser, generated state lives under `System/`, commands report failure honestly, and no hidden cloud fallback receives note contents. The workflow is detailed in [the protocol](../System/PROTOCOL.md) and [automation model](../System/AUTOMATION.md).

Agent identity belongs to the external tool, not Zephyr core. One agent may operate a task at a time; additional agents are optional, temporary reviewers or specialists, never a permanent hierarchy.
