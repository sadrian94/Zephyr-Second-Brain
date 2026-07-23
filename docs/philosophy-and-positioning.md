# Zephyr v0.2.2: Manual-First, Local-First

Capture should be easy; commitments should be visible. Zephyr separates the two.

The system accepts unstructured material in `Capture/`, durable knowledge in `Brain/`, explicitly chosen work in `Active/`, and historical records in `Archive/`. A proposal is not a commitment: an agent can offer structure, but the human decides whether it becomes active work or an archive record.

This choice is intentionally less magical. It makes the important mechanisms inspectable: Markdown is the record, YAML is parsed with a standard parser, commands report failure honestly, and no hidden cloud fallback receives note contents. The workflow is detailed in [the protocol](../System/PROTOCOL.md).

Agent identity belongs to the external tool, not Zephyr core. One agent may operate a task at a time; additional agents are optional, temporary reviewers or specialists, never a permanent hierarchy.
