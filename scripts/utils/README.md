# ACE logs

The scripts in this folder read the logs of an ACE run. For each task, ACE runs three LLM roles in turn:

1. **Generator.** Solves the task step by step, writing code and reading what the environment returns. Every Generator call has the whole playbook in its prompt, between `### PLAYBOOK BEGIN` and `### PLAYBOOK END`.
2. **Reflector.** After the task, writes an analysis of what went wrong (`error_identification`, `root_cause_analysis`, and more).
3. **Curator.** Reads the Reflector's analysis and proposes changes to the playbook. In these runs it only issues `ADD` operations, each one a new bullet.

The playbook after a task is the starting playbook of the next task.

## What is saved for a task

The logs of a task are stored in `<run folder>/tasks/<id>/`, where the id looks like `<family>_<n>`, for example `d0b1f43_1`. This folder contains:

- `logs/lm_calls.jsonl`: every LLM call of the task, one per line.
- `logs/environment_io.md`: the code the Generator ran and what the environment returned.
- [`evaluation/report.md`](#evaluationreportmd): the evaluation result.

## evaluation/report.md

AppWorld writes this report when it evaluates a task. A task with no `evaluation/report.md` counts as unfinished.

The evaluation is a short list of checks on the task's outcome, for example `assert answers match.` (the agent's answer equals the task's stored ground truth answer) and `assert no model changes.` (the app data was not changed when it should not be). Each task has its own checks, and a task passes only when all of them pass.

The report has three parts:

- **Overall Stats.** Three numbers: `Num Passed Tests`, `Num Failed Tests` and `Num Total  Tests`.
- **Passes.** One `>> Passed Requirement` entry per check that passed, with its description.
- **Fails.** One `>> Failed Requirement` entry per check that failed, with its description and the code of the check. It says `None` when nothing failed.

Example of a failed task:

````
Num Passed Tests : 1
Num Failed Tests : 1
Num Total  Tests : 2

>> Passed Requirement
assert no model changes.

>> Failed Requirement
assert answers match.
```python
with test(
    """
    assert answers match.
    """
):
    test.case(ground_truth_answer, "==", predicted_answer, normalize=float, tolerance=0.51)
```
````

A task passed when `Num Failed Tests` is 0 and `Num Passed Tests` equals `Num Total  Tests`.
