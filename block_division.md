# Block division

- date: 2026-11-09
- coherence: 2026-11-09

## Blocks

### Block 1: shared (src/shared/: models.py, defaults.py)
- receives: nothing (no other block, no external source)
- processes: nothing at runtime; defines the shared data structures and values
- delivers: the pydantic models of spec point 4.9 (data models), the internal models (Chunk with its text and character range, the settings of each index version), the default values and the fixed limits (e.g. max_chunk_size ceiling 2000)
- depends on: no block

## Diagram (Mermaid)

```mermaid
flowchart LR
    shared[shared: models and defaults]
```

## Decided

- Block 1 holds only shared data: the spec point 4.9 models, the internal models (Chunk, index version settings) and the defaults and fixed limits.
- Defaults in block 1 never replace CLI arguments: every path still comes from a CLI argument (prohibitions 3: no hard-coded input/output paths). Values computed at runtime (N, number of chunks of the active index; T, time of one answer on CPU) are not in block 1.
- Block 1 is named shared: package src/shared/ with models.py (pydantic models) and defaults.py (defaults and fixed limits).
- The interfaces of spec point 7 (retriever, chunker, generator) are not in block 1: each one goes in the block that implements it.

## Pending

- Blocks 2 onward: not proposed yet (the user proposes them block by block, row 403 of workflow).
