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

Differences from the paper:

1. **Agent LLM:** `deepseek-v4-flash-0731`, not Qwen3-8B/14B/32B.
2. **Repetitions:** each task runs 4 times (Avg@4 and Pass@4). The paper repeats that 3 times (12 runs per task) and reports the average.
3. **Self-reflection:** the default `num_trials = 1` means no retries after a failure. The paper's maximum is 3. It is unclear whether the paper's "fixed" row used retries.
4. **Tasks:** a 9-task pilot subset, not all 168. These tasks are in the train split, so they overlap with the pool.
5. **Embedding model:** `text-embedding-3-small` at 1536 dimensions, not `text-embedding-v4` at 1024.

## 5. Configure the run

All settings are set on the command line in step 6:

| Option | Meaning |
|---|---|
| `--mode` | `fixed` (default), `dynamic` or `none` (no memory) |
| `--model_name` | agent model |
| `--num_runs` | attempts per task (paper: 4) |
| `--max_workers`, `--batch_size` | parallelism; lower them if the API rate-limits |

The initial pool is `docs/library/paper_data/task/appworld_qwen3_8b.jsonl`. A run is one pass over all tasks (`--num_runs 4` means 4 passes). In `dynamic` mode the pool changes as tasks finish, so it is reset to the initial pool before each run.

## 6. Run (terminal 2)

```bash
cd ReMe-v0.3.1.10/benchmark/appworld
conda activate appworld-reme
python run_appworld.py --mode fixed --model_name deepseek-v4-flash-0731 --num_runs 4
python run_exp_statistic.py
```

Results: `exp_result/<model>/*.jsonl`. A task is solved when `after_score == 1`.

## Known issue: Ray

`run_appworld.py` uses Ray. In our tests Ray 2.59 did not start in the AppWorld environment. Options: try an older Ray (untested), or replace Ray with a plain multiprocessing runner (worked in a 6-task test).
