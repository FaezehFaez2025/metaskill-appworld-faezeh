# Notes: ReMe v0.3.1.10 (AppWorld baseline)

---

## 1. Version used

**Decision:** ReMe `v0.3.1.10` (commit `36a5512`, 2026-06-03), the last release with the AppWorld benchmark.
Source: https://github.com/agentscope-ai/ReMe

**Rationale:**
- The paper reports AppWorld results, but ReMe 0.4.0 (a rewrite, 2026-06-22) removed the AppWorld code, so the current ReMe has none.
- Version `v0.3.1.10` has the paper's full method, the AppWorld runner, and the released experience pools.
- 8 untagged commits (June 4-19) came after `v0.3.1.10`. We use `v0.3.1.10` and not the later commits: it is an official release, and those commits are unfinished work on the 0.4.0 rewrite. They did not change the AppWorld code, the memory pipeline or the pools.

---

## 2. Initial experience pools

The paper builds one initial pool per model from the 90 AppWorld training tasks. The released pools are in `docs/library/paper_data/task/`:

| File | Experiences |
|---|---|
| `appworld_qwen3_8b.jsonl` | 207 |
| `appworld_qwen3_14b.jsonl` | 218 |
| `appworld_qwen3_32b.jsonl` | 184 |

We use these released pools and do not build our own. `benchmark/appworld/run_appworld.py` loads the 8B one by default.

---

## 3.

**Decision:**

**Rationale:**
