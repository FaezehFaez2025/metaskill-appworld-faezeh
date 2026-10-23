# Run ReMe on AppWorld (test_normal, 168 tasks)

Steps for `ReMe v0.3.1.10` with the released experience pool and DeepSeek as the executor.
Paths are relative to the repo root `metaskill-appworld-faezeh/`.

## 1. Environments

Two separate conda environments.

```bash
cd ReMe-v0.3.1.10

# ReMe service
conda create -y -n reme-paper python=3.12
conda activate reme-paper
pip install .
pip install "agentscope==1.0.20" greenlet
pip uninstall -y fastmcp fastmcp-slim mcp-types
pip install --no-cache-dir "fastmcp==2.14.1" "mcp==1.25.0"

# AppWorld agent
conda create -y -n appworld-reme python=3.12
conda activate appworld-reme
pip install appworld ray openai jinja2 loguru python-dotenv tqdm pandas requests
appworld install
```

## 2. AppWorld data

```bash
cd ReMe-v0.3.1.10/benchmark/appworld
appworld download data
```

## 3. Keys

Build `ReMe-v0.3.1.10/.env` (git-ignored) from the key in the root `.env`. The service and the agent both read it.

```bash
cd ReMe-v0.3.1.10
set -a; . ../.env; set +a
printf 'LLM_API_KEY=%s\nLLM_BASE_URL=%s\nEMBEDDING_API_KEY=%s\nEMBEDDING_BASE_URL=%s\nOPENAI_API_KEY=%s\nOPENAI_BASE_URL=%s\n' \
  "$OPENAI_API_KEY" "$OPENAI_BASE_URL" "$OPENAI_API_KEY" "$OPENAI_BASE_URL" "$OPENAI_API_KEY" "$OPENAI_BASE_URL" > .env
chmod 600 .env
```

Never commit keys.

## 4. Start the ReMe service (terminal 1)

Start from the `ReMe-v0.3.1.10` root: the pool path in step 5 is relative to it.

```bash
cd ReMe-v0.3.1.10
conda activate reme-paper
set -a; . ./.env; set +a
reme2 backend=http http.host=127.0.0.1 http.port=8002 \
  llms.default.model_name=deepseek-v4-flash-0731 \
  embedding_models.default.model_name=text-embedding-3-small \
  embedding_models.default.dimensions=1536 \
  vector_stores.default.collection_name=appworld_test
```

The paper's embedding model `text-embedding-v4` is not available on our endpoint, so `text-embedding-3-small` is used.

## 5. Configure the run

Edit `main()` in `benchmark/appworld/run_appworld.py`:

| Setting | ReMe fixed | ReMe dynamic | No memory |
|---|---|---|---|
| `use_memory` | `True` | `True` | `False` |
| `use_memory_addition` | `False` | `True` | - |
| `use_memory_deletion` | `False` | `True` | - |

Also set `model_name = "deepseek-v4-flash-0731"` and `num_runs` (paper: 4). Lower `max_workers` and `batch_size` if the API rate-limits.

The initial pool is `docs/library/paper_data/task/appworld_qwen3_8b.jsonl`. For dynamic mode, move `load_memory(...)` inside the loop over runs so every run starts from the same pool.

## 6. Run (terminal 2)

```bash
cd ReMe-v0.3.1.10/benchmark/appworld
conda activate appworld-reme
python run_appworld.py
python run_exp_statistic.py
```

Results: `exp_result/<model>/*.jsonl`. A task is solved when `after_score == 1`.

## Known issue: Ray

`run_appworld.py` uses Ray. In our tests Ray 2.59 did not start in the AppWorld environment. Options: try an older Ray (untested), or replace Ray with a plain multiprocessing runner (worked in a 6-task test).
