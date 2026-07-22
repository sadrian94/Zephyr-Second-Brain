---
type: note
tags: [dashboard]
cssclasses: [dashboard]
---
# Active Projects

```dataview
TABLE priority AS Priority, deadline AS Deadline, area AS Area
FROM "Active"
WHERE type = "project"
SORT deadline ASC
```

Projects arrive here only through the explicit `activate --approve` command. See the Home dashboard and `System/PROTOCOL.md`.
