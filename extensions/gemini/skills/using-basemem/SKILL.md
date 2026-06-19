---
name: using-basemem
description: BaseMem — 3 tools
---

# BaseMem — 3 tools

## Memory (optional)
`basemem-memory_get_agent_context(project='folder')` — past state/decisions.
Only needed for session recovery; otherwise skip.

## Code
`basemem-memory_code_find('symbol')` — finds everything. Auto-indexes. Single match = detail+callers.
**Never Read to find something. This replaces Read.**

## Write
`basemem-memory_log_interaction(topic, decision, current_state, next_step, activity)` — only when state changes.
