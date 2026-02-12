# DocumentCanvas `execCommand` Migration Plan

## 1) Existing `document.execCommand` usage inventory

The legacy toolbar used these commands:

- `bold`
- `italic`
- `underline`
- `strikeThrough`
- `formatBlock` (`h1`, `h2`, `h3`, `p`)
- `insertUnorderedList`
- `insertOrderedList`
- `undo`
- `redo`

The canonical mapping is now codified in `LEGACY_EXEC_COMMANDS` for compatibility fallback.

## 2) Selected modern implementation

We are adopting an **Input Events Level 2 + DOM Range adapter** as an intermediate modern stack:

- Uses `beforeinput` `inputType` mapping for standard formatting intents.
- Uses DOM `Selection`/`Range` APIs for deterministic formatting operations.
- Keeps a narrow fallback to `execCommand` only when a command cannot be applied with Range logic.

This avoids immediate dependency weight and schema migration costs from TipTap/ProseMirror/Lexical while still removing primary reliance on `execCommand`.

## 3) Migration adapter details

`richTextAdapter.ts` implements:

- Command enum (`FormattingCommand`) mapped from toolbar and `beforeinput`.
- Inline formatting wrappers (`strong`, `em`, `u`, `s`).
- Block conversion (`h1`, `h2`, `h3`, `p`).
- List conversion (`ul`/`ol` + `li`).
- Adapter-level history (`undo`/`redo`) snapshots.
- Legacy command fallback (`LEGACY_EXEC_COMMANDS`) as safety net.

This preserves user-visible UX (same toolbar, same keyboard intent support) and content format compatibility (HTML output with sanitizer pass).

## 4) Phased rollout

If compatibility transformations become necessary, rollout in phases:

1. **Phase A (current)**: Adapter on by default with legacy fallback and telemetry/logging hooks.
2. **Phase B**: Add optional feature flag for a schema editor (TipTap/ProseMirror/Lexical) behind dual-write (HTML + schema JSON).
3. **Phase C**: Backfill converter for legacy HTML edge cases and validate via sampled artifact replay.
4. **Phase D**: Disable fallback `execCommand`, keep read-compat parser.
5. **Phase E**: Remove compatibility code once artifact corpus migration SLOs pass.

