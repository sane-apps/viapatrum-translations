# Claims — who is working on what

Take the next free slice:

```bash
python3 scripts/claims.py start --agent YourName
```

That locks the top `free` row. One slice per person. Statuses: `free` → `claimed` → `prepped` (machine crib) or `done` (human Pass B).  
If a `claimed` row is older than 48 hours with no handoff, anyone may set it back to `free`.

## Open / active claims

| Claim ID | Status | Book slug | Slice (sections) | Agent | Started | Branch | Notes |
|----------|--------|-----------|------------------|-------|---------|--------|-------|
| grace-assist-mine | claimed | ante-nicene-topics | Grace-and-assistance: one new locked-source excerpt + stance | StephanMini | 2026-09-12 | wip/grace-assist-mine | Topics lane |

