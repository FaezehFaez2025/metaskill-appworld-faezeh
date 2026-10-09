# Run ACE online on the 18-task AppWorld pilot

## 1. Get the app bundles

Copy the bundles from Jiayao's folder:

```bash
SRC=/home/jiayao/Metaskill-library/baselines/ace/ace-appworld
cp "$SRC/src/appworld/.source/apps.bundle" src/appworld/.source/apps.bundle
cp "$SRC/src/appworld/.source/tests.bundle" src/appworld/.source/tests.bundle
cp "$SRC/generate/.source/data.bundle" generate/.source/data.bundle
cp "$SRC/generate/.source/tasks.bundle" generate/.source/tasks.bundle
```

Check one file. It must say `data`, not `ASCII text`:

```bash
file src/appworld/.source/apps.bundle
```

## 2. Create the environment

Use Python 3.11 or newer. This machine has Python 3.12, and the completed run used 3.12.

```bash
python3 -m venv .venv-clean-appworld
source .venv-clean-appworld/bin/activate

python -m pip install --upgrade pip setuptools wheel
pip install -e .
pip install -e "experiments[simplified]"
```

Then run:

```bash
python -m pip install \
  'pydantic==2.10.6' \
  'pydantic-core==2.27.2' \
  'litellm==1.74.9' \
  'click==8.1.8' \
  'openai==1.109.1' \
  'httpx==0.27.2' \
  'typer==0.12.5' \
  'huggingface-hub==0.26.5'
```

Check, then unpack the apps and download the tasks:

```bash
python -c "import click; print('click', click.__version__)"
python -c "import appworld; print('appworld ok')"
appworld install --repo
appworld download data
```

`click` must print `8.1.8`, and `appworld ok` must print.

## 3. API key

```bash
cp /home/jiayao/Metaskill-library/baselines/ace/.env .env
```

## 4. Run the 18 tasks

```bash
source .venv-clean-appworld/bin/activate
export APPWORLD_PROJECT_PATH="$(pwd)"

appworld run "ACE_18_task_online_no_GT_pilot/deepseek-v3"
```

That run uses DeepSeek-v3, no ground-truth code, at most 40 steps, these 18 tasks, and updates the playbook after each task:

`07b42fd_1` `07b42fd_2` `07b42fd_3` `e3d6c94_1` `e3d6c94_2` `e3d6c94_3` `76f2c72_1` `76f2c72_2` `76f2c72_3` `2a163ab_1` `2a163ab_2` `2a163ab_3` `3c13f5a_1` `3c13f5a_2` `3c13f5a_3` `d0b1f43_1` `d0b1f43_2` `d0b1f43_3`

## 5. Where the logs are

`experiments/outputs/` is gitignored, so the editor file search will not show it.

```text
experiments/outputs/ACE_18_task_online_no_GT_pilot/deepseek-v3/
  trained_playbook.txt
  tasks/<task_id>/
    evaluation/report.md
    logs/lm_calls.jsonl
    logs/loggger.log
    logs/environment_io.md
    logs/api_calls.jsonl
```

`evaluation/report.md` says whether the task passed. `logs/lm_calls.jsonl` stores every model call, including the Reflector and the Curator. `trained_playbook.txt` is the playbook after the latest update.

## 6. Check whether the update wrote a lesson

After all 18 tasks have finished, and with the same virtual environment still active:

```bash
python3 scripts/analyze_ace_playbook_update.py
```

The script does not call a model. It reads `evaluation/report.md` and `logs/lm_calls.jsonl`. A new lesson is a bullet id that appears in the next task's playbook and was absent from the current one. "Used" means the next task's own replies contain the first 80 characters of that bullet. The bullet sitting in the prompt does not count.

The report is printed and saved to

`experiments/outputs/ACE_18_task_online_no_GT_pilot/deepseek-v3/update_transfer.md`.
