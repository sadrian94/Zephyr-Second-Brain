# Project Management in v0.3.1

`Active/` contains only projects the user deliberately chose to advance. Create or propose work in `Capture/`; a proposal is not an active project.

Before activation, a project must have valid YAML: `type: project`, an allowed status and priority, an ISO deadline, and an area. Preview then apply the move with `activate --approve`. When it is completed or stopped, update the status and use `archive --approve`. No watcher, agent procedure, or status edit archives it automatically.

See [the protocol](../System/PROTOCOL.md) for the commands and approval boundary.
