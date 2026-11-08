# Output quality rubric (blind review)

Scores the code a harness produced, independent of speed and tokens. Every run already passes
its hidden tests, so correctness is not scored here; the rubric separates "passes" from "good".

Each criterion is scored 0, 1 or 2. Max 12.

| # | Criterion | 2 | 1 | 0 |
|---|---|---|---|---|
| 1 | Robustness | Error paths handled where the spec implies them (bad input rejected, resources released, transaction boundaries clear) | Minor gap (e.g. connection never closed, unchecked decode) | Obvious hole that would bite a real user |
| 2 | Spec coverage by tests | Every numbered requirement in TASK.md has at least one test that would fail if it were removed | One requirement untested | Several untested |
| 3 | Test quality | Each test has one distinct purpose; name and body agree; no copy tests for the same requirement; no pinning of implementation details the spec does not dictate | One redundant or mislabeled test | Padding: several redundant tests, or tests that assert nothing meaningful |
| 4 | Documentation | README explains what a user needs (new default, new commands, migration) in the existing README's voice and length | Present but thin, or over-long | Missing or wrong |
| 5 | Spec fidelity, no slop | Does what was asked and nothing else; every extra line serves a requirement | Some unrequested scope or boilerplate | Over-engineered, speculative abstractions, or requirements silently reinterpreted |
| 6 | Consistency with the codebase | Matches the existing module's style, naming, typing and structure; reads as if the original author wrote it | Small style drift | Foreign style, duplicated helpers, broken conventions |

Rules for the grader:

- Length is not quality. A longer diff must justify every extra block against a requirement; otherwise it loses on criterion 5.
- Read test bodies, not test names. A test whose name promises something its body does not check is slop (criterion 3).
- Judge against TASK.md only. Do not reward features the task did not ask for.
- Score each submission on its own, then re-check that equal work got equal scores across submissions.
- Output one line of justification per criterion; the justification must cite something in the diff.

Procedure: `bin/blind.sh` copies each run's `diff.patch` to `blind/<task>/S<nn>.patch` in random order and
writes the mapping to `blind/<task>/KEY.json` (not shown to graders). Two independent graders score every
submission of a task; the final score is their mean. `bin/quality.py` joins scores with `runs/*/result.json`.
