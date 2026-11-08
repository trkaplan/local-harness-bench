# Coding-agent harness benchmark on the local Qwen3.8-Flash-Next (2026-11-08)

Four open-source coding agents, each built from source on the M5 and pointed at the local oMLX
endpoint (`http://127.0.0.1:8018/v1`, model `qwen-flash-next`, thinking off, non-thinking sampling).
Question: which harness drives the local model best, and does any of them phone home?

| Harness | Pinned revision | Build | Entry used |
|---|---|---|---|
| Pi (earendil-works/pi) | v1.5.0 | `npm install --ignore-scripts && npm run hydrate:model-data && npm run build:offline` | `dist/bundle/cli.js --print` |
| opencode (anomalyco/opencode) | v2.2.6 | `bun install && bun run build --single` in `packages/cli` | `opencode run` |
| mini-swe-agent (SWE-agent) | v2.4.6 | uv venv + `pip install -e .` (+ `mcp`, missing from litellm's deps) | `mini -y --exit-immediately` |
| deepseek-harness (deepseek-ai) | master fcc0ad4 (0.2.2-rc.1, 2026-11-04) | `pnpm install --frozen-lockfile && pnpm run build` | `dsh --profile headless` |

Everything lives in `~/local-ai/harness/`: `src/` (clones), `cfg/` (per-harness config, isolated from `~`),
`bin/` (`run-one.sh`, `queue.sh`, `netwatch.sh`, `summary.py`), `tasks/` (fixtures + hidden tests), `runs/` (every run: stdout, stderr, diff, oMLX request log, result.json).

## Telemetry audit

Method: source grep for analytics SDKs and hostnames, then every run under `netwatch.sh`, which samples
`lsof` on the harness process tree every 0.3 s and records any non-loopback connection.

| Harness | What it wants to call | How it is switched off here | Observed |
|---|---|---|---|
| Pi | pi.dev version check, model-catalog refresh, install/update telemetry + attribution headers | `PI_OFFLINE=1 PI_SKIP_VERSION_CHECK=1 PI_TELEMETRY=0`. Catalog is fetched once at build time (models.dev, OpenRouter, Vercel, NVIDIA; read-only) | 0 external connections in 4 runs |
| opencode | first run opened a TLS connection to opencode.ai (Cloudflare 172.66.173.149): built-in "opencode" provider / free-models and model catalog fetch. No telemetry SDK found. | `OPENCODE_DISABLE_FREE_MODELS=1 OPENCODE_DISABLE_MODELS_FETCH=1 OPENCODE_DISABLE_AUTOUPDATE=1 DO_NOT_TRACK=1`, `"update":"disable"`, `"share":"disabled"`, `"disabled_providers":["opencode"]` | 0 external connections in 4 runs (and in a fresh-cache check) |
| mini-swe-agent | none of its own; litellm fetches a model-cost map from GitHub | `LITELLM_LOCAL_MODEL_COST_MAP=True MSWEA_COST_TRACKING=ignore_errors` | 0 external connections in 4 runs |
| deepseek-harness | OTel product/session telemetry to dsh-otel-collector.deepseeksvc.com (feedback-gated), `dsh_session_log` upload inside DeepSeek API requests (default on, DeepSeek adapter only), plugin inventory, web search/fetch via DeepSeek API, CoT translation via Bing (web UI only, user-triggered) | home patch `cfg/dsh/cordis.patch.yml`: pi-ai route to oMLX, `session-log-deepseek.enabled=false`, otel / inventory / web-deepseek / llm-deepseek plugins disabled; env `DSH_TELEMETRY_DISABLED=1 DSH_TELEMETRY_MODE=DISABLED` | 0 external connections in 4 runs |

## Tasks

Both tasks are Python fixtures with a visible test suite and a hidden one that is copied in only after the agent exits.

- **A, bug fix** (`tasks/a-bugfix`): three documented bugs in a 70-line ledger module + a rounding invariant; 7 hidden tests.
- **B, feature** (`tasks/b-feature`): add a SQLite backend to a JSON-backed todo CLI, a store factory, a `migrate` subcommand with a non-empty-destination guard, a `rename` command, tests and README; 11 hidden tests.

Prompt text: `tasks/*/TASK.md` plus one line telling the agent which interpreter has pytest. Each harness ran each task twice, sequentially (oMLX `max_concurrent_requests` 1), with a 30-minute timeout. Tokens and call counts come from oMLX `/admin/api/stats` deltas.

## Results

| harness | task | run | wall s | LLM calls | prompt tok | compl tok | len cut | hidden | visible | ext conns | exit |
|---|---|---|---|---|---|---|---|---|---|---|---|
| dsh | a-bugfix | 1 | 114 | 26 | 315854 | 7512 | 0 | 7 passed in 0.01s | 8 passed in 0.00s | 0 | 0 |
| dsh | a-bugfix | 2 | 132 | 25 | 288965 | 7678 | 0 | 7 passed in 0.00s | 8 passed in 0.00s | 0 | 0 |
| dsh | b-feature | 1 | 213 | 38 | 640831 | 12820 | 0 | 11 passed in 0.03s | 18 passed in 0.03s | 0 | 0 |
| dsh | b-feature | 2 | 205 | 33 | 519295 | 11843 | 0 | 11 passed in 0.03s | 28 passed in 0.03s | 0 | 0 |
| mini | a-bugfix | 1 | 43 | 9 | 40884 | 2447 | 0 | 7 passed in 0.00s | 9 passed in 0.00s | 0 | 0 |
| mini | a-bugfix | 2 | 41 | 11 | 42917 | 2191 | 0 | 7 passed in 0.00s | 8 passed in 0.00s | 0 | 0 |
| mini | b-feature | 1 | 59 | 11 | 57500 | 3843 | 0 | 11 passed in 0.03s | 13 passed in 0.02s | 0 | 0 |
| mini | b-feature | 2 | 63 | 11 | 57665 | 3732 | 0 | 11 passed in 0.03s | 11 passed in 0.02s | 0 | 0 |
| opencode | a-bugfix | 1 | 40 | 11 | 110212 | 2544 | 0 | 7 passed in 0.00s | 9 passed in 0.00s | 0 | 0 |
| opencode | a-bugfix | 2 | 40 | 10 | 94544 | 2048 | 0 | 7 passed in 0.00s | 8 passed in 0.00s | 0 | 0 |
| opencode | b-feature | 1 | 81 | 17 | 212204 | 4961 | 0 | 11 passed in 0.03s | 17 passed in 0.02s | 0 | 0 |
| opencode | b-feature | 2 | 92 | 21 | 261157 | 5007 | 0 | 11 passed in 0.03s | 14 passed in 0.03s | 0 | 0 |
| pi | a-bugfix | 1 | 26 | 9 | 29538 | 1859 | 0 | 7 passed in 0.00s | 9 passed in 0.00s | 0 | 0 |
| pi | a-bugfix | 2 | 30 | 9 | 29337 | 1792 | 0 | 7 passed in 0.00s | 9 passed in 0.00s | 0 | 0 |
| pi | b-feature | 1 | 62 | 18 | 83136 | 3981 | 0 | 11 passed in 0.03s | 14 passed in 0.02s | 0 | 0 |
| pi | b-feature | 2 | 70 | 19 | 95787 | 4143 | 0 | 11 passed in 0.03s | 13 passed in 0.02s | 0 | 0 |

| harness | task | runs | mean wall s | mean calls | mean prompt tok | hidden pass |
|---|---|---|---|---|---|---|
| dsh | a-bugfix | 2 | 123 | 25.5 | 302410 | 2/2 |
| dsh | b-feature | 2 | 209 | 35.5 | 580063 | 2/2 |
| mini | a-bugfix | 2 | 42 | 10.0 | 41900 | 2/2 |
| mini | b-feature | 2 | 61 | 11.0 | 57582 | 2/2 |
| opencode | a-bugfix | 2 | 40 | 10.5 | 102378 | 2/2 |
| opencode | b-feature | 2 | 86 | 19.0 | 236680 | 2/2 |
| pi | a-bugfix | 2 | 28 | 9.0 | 29438 | 2/2 |
| pi | b-feature | 2 | 66 | 18.5 | 89462 | 2/2 |

All 16 runs passed every hidden test, no run hit the 16K output cap, no run opened an external connection.

## Reading the numbers

- **Pi** is the fastest and, after mini, the cheapest: 28 s / 66 s and 29K / 89K prompt tokens. Compact system prompt (1.8K tokens), reads only what it needs.
- **mini-swe-agent** uses the fewest tokens (42K / 58K) with only a bash tool, and was never slower than opencode. The price is a weaker edit workflow (heredocs via bash), which showed in no failure here.
- **opencode** is as fast as Pi on the short task but burns 3x the prompt tokens (its first turn is only 750 tokens, so the cost is in extra round trips and re-sent context).
- **deepseek-harness** is the slowest and most expensive by far: 2 to 3.5 minutes and 300K / 580K prompt tokens per task, mostly a 6.4K-token system prompt resent on 25 to 38 calls. In exchange its output was the most thorough: explicit BEGIN/COMMIT transaction with rollback, defensive row decoding, 15 tests and a 45-line README section for task B; the most careful `parse_amount` rewrite for task A (rejects trailing or embedded minus signs too).
- Code quality otherwise: all four produced the same schema, the same `DELETE + INSERT` full rewrite inside one transaction (`with conn:` in Pi/opencode/mini), the same factory and the same CLI shape. opencode and mini guard `load()` with an exists check, Pi creates the database on first read; none of this is wrong per the spec.
- Model speed during the runs: 70 to 135 tok/s decode on individual requests, consistent with the 30 October soak.

## Caveats

- Two runs per cell and two tasks: enough to rank cost and speed, not enough to measure success rate; the model solved everything, so the harnesses were not stressed on recovery from failure.
- Thinking was turned off server-side (`enable_thinking=false` on the model) for the benchmark so all harnesses were identical; it is back on. Pi, opencode and mini also send `chat_template_kwargs.enable_thinking=false` per request; deepseek-harness does not expose a way to send it, so with thinking on it will reason on every turn.
- The opencode driver was patched mid-run once (the timeout watcher held the queue pipe open for 30 minutes after a 40-second run); the affected mini run was discarded and repeated. Wall times in the table are per-run measurements and were not affected.
- netwatch samples lsof at 0.3 s; a connection shorter than that could be missed. The first-run opencode connection was caught at that resolution, and the fixes were verified against a fresh cache.

## Output quality (blind review, added later the same day)

Passing the hidden tests says nothing about slop, so every diff was scored against `~/local-ai/harness/RUBRIC.md`:
six criteria at 0–2 each (robustness, spec coverage by tests, test quality, documentation, spec fidelity / no slop,
consistency with the codebase), max 12. Harness names were stripped (`bin/blind.sh`, random S01–S08 ids per task)
and two independent Claude graders scored each set; the two agreed exactly on 12 of 16 totals and were never more than 1 point apart.
One packaging bug was fixed on the way: the very first run (pi-a-bugfix-1) predated the `__pycache__` exclusion, so
its diff contained `.pyc` files from our own hidden-test run; the packet was rebuilt and both graders re-scored it.

| harness | task | quality /12 | wall s | prompt tok | quality per 100K tok | quality per min |
|---|---|---|---|---|---|---|
| pi | a-bugfix | 9.2 | 28 | 29,438 | 31.4 | 19.8 |
| pi | b-feature | 10.0 | 66 | 89,462 | 11.2 | 9.1 |
| mini | a-bugfix | 9.8 | 42 | 41,900 | 23.3 | 13.9 |
| mini | b-feature | 10.0 | 61 | 57,582 | 17.4 | 9.8 |
| opencode | a-bugfix | 9.5 | 40 | 102,378 | 9.3 | 14.2 |
| opencode | b-feature | 10.5 | 86 | 236,680 | 4.4 | 7.3 |
| dsh | a-bugfix | 9.2 | 123 | 302,410 | 3.1 | 4.5 |
| dsh | b-feature | 6.2 | 209 | 580,063 | 1.1 | 1.8 |

| harness | quality /12 (both tasks) | per 100K tok | per min |
|---|---|---|---|
| pi | 9.6 | 16.2 | 12.3 |
| mini | 9.9 | 19.9 | 11.5 |
| opencode | 10.0 | 5.9 | 9.5 |
| dsh | 7.8 | 1.8 | 2.8 |

What the graders found (per-criterion notes in `blind/*/grader*.json`):

- **deepseek-harness's "thoroughness" is mostly slop.** On task B both runs scored lowest (6, 6.5): copy tests for
  requirements already covered, a test named `test_migrate_failure_creates_no_destination_file` whose body never
  checks that, a "byte for byte" roundtrip test that compares parsed JSON, speculative `None`/non-list handling for
  NOT NULL columns, manual BEGIN/COMMIT where `with conn:` suffices, and a 3-line README turned into 40+. On task A
  one run was the best patch of all 16 (11: documented the new ValueError contract, module-level imports), the other
  the worst (7.5: its `if "-" in s` runs after currency stripping, so `€ -3.10` and `$-5`, accepted by the original,
  now raise). High variance, high cost.
- **Pi, mini and opencode are within 0.4 points of each other** and nearly interchangeable in style; all three sit
  in the "minimal, consistent" group the graders described. The shared gap: none of them wrote a test for
  requirement 3 of task B (default `~/.todo.db` / `TODO_FILE`); only dsh and one opencode run did. Pi also never
  closes its SQLite connection (`with conn:` commits but does not close) and drops the `exists()` guard in `load()`,
  which cost it the robustness point on task B; mini closes in `try/finally`.
- **mini's one structural oddity:** one run dispatches `migrate` by sniffing `argv[0]` with a second ArgumentParser
  while also registering a `migrate` subparser (9 instead of 11).
- Six of eight task-A patches put `import pytest` inside the test body instead of at module top: a model habit, not
  a harness one, scored uniformly as minor drift.

Revised reading: quality is a wash between Pi, mini and opencode, so the ranking is decided by cost. **Pi** gives the
most quality per minute, **mini** the most per token (20 vs 16 per 100K), opencode burns 3x the tokens for the
same result, and dsh is both the most expensive and, on the larger task, the worst. The earlier remark that dsh's
output was "the most thorough" does not survive the rubric; it was the longest.

## Prompt-rule experiment (same evening)

Question: can a one-sentence instruction give Pi, mini and opencode the one thing dsh did better (a test for every
numbered requirement) without dsh's padding? Task B only, two runs per cell, hidden tests passed in every run.

Two wordings, two placements. v1 (`tasks/RULES-coverage.md`): "make sure at least one test would fail if that
requirement were removed. One focused test per requirement is enough: do not add tests beyond that, do not
duplicate checks, keep the diff minimal". v2 (`RULES-coverage-v2.md`): "check that every numbered requirement has at
least one direct test of its own", same tail. Placement: appended to the task prompt (`RULES=` in `run-one.sh`), or
in the harness's own system prompt (`SYSRULES=`: Pi `--append-system-prompt`, mini `agent.system_template`,
opencode `instructions` in a separate config dir). Reaching the model was verified for all three.

| harness | variant | wall s | prompt tok | lines | tests (run1/run2) | req-3 test |
|---|---|---|---|---|---|---|
| pi | base | 66 | 89,462 | 224 | 11/10 | 0/2 |
| pi | v1 prompt | 174 | 506,615 | 199 | 11/6 | 1/2 |
| pi | v2 system | 58 | 88,168 | 207 | 9/8 | 0/2 |
| pi | v2 prompt | 58 | 102,212 | 144 | 5/4 | 0/2 |
| mini | base | 61 | 57,582 | 236 | 10/8 | 0/2 |
| mini | v1 prompt | 58 | 76,618 | 174 | 7/6 | 2/2 |
| mini | v2 system | 53 | 52,238 | 194 | 7/8 | 0/2 |
| mini | v2 prompt | 74 | 90,491 | 148 | 5/4 | 0/2 |
| opencode | base | 86 | 236,680 | 263 | 14/11 | 1/2 |
| opencode | v1 prompt | 117 | 353,780 | 183 | 7/10 | 2/2 |
| opencode | v2 system | 92 | 149,291 | 196 | 10/8 | 0/2 |
| opencode | v2 prompt | 95 | 234,124 | 130 | 0/6 | 0/2 |

Blind rubric scores (6 baseline + 6 variant patches mixed per set, two graders; only within-set differences are
meaningful, the same baseline patch moved up to 2 points between sets):

- v1 prompt vs base: Pi 10.0 → 10.0, mini 9.5 → 9.2, opencode 10.0 → 8.5. Spec coverage 1.17 → 1.83 but test
  quality 1.92 → 1.17 and consistency 1.75 → 1.33: the model read "one focused test per requirement, no more" as
  "fewer tests" and bundled two or three requirements per function (`test_cli_rename_and_default_file`), plus lazy
  imports inside `open_store`. Pi's first run took "would fail if removed" literally and did manual mutation testing:
  62 calls, 949K tokens, 5 minutes, and the best patch of the set (11).
- v2 system vs base: Pi 8.2 → 9.5, mini 9.2 → 9.5, opencode 9.2 → 9.5, gained on docs and consistency, not on
  coverage (1.17 → 1.00). Requirement 3 was never tested.
- v2 prompt: not graded; test counts fell to 4–6 and one opencode run added neither tests nor the README change (requirement 6 skipped entirely), so coverage is worse
  than baseline by inspection.

Reading: the active ingredient was v1's "would fail if that requirement were removed", which forces the model to map
tests to requirements; the "one test is enough, no more" tail is what produced the bundling. v2 kept the tail and
dropped the active part, so it only shrank the test suites. System-prompt placement was not weaker per se (v2 system
beat v2 prompt), but no v2 variant moved coverage. Next wording to try: keep the mutation framing, drop the cap:
"for every numbered requirement, add one test that would fail if that requirement were removed; name each test after
its requirement". With this model, the cap sentence is what to leave out.

Also found: a stale `opencode serve --service` from the afternoon made every later `opencode run` fail with HTTP 500
until killed. `run-one.sh` now kills it after each opencode run and every queue ends with `bin/check-leftovers.sh --kill`.

## Recommendation

For day-to-day coding against the local model: **Pi** as the default (fastest, clean, ships `--print` and JSON modes, Anthropic and OpenAI protocols), **mini-swe-agent** for batch jobs where token budget matters more than editing comfort; the blind review puts their output quality level. deepseek-harness is worth revisiting once it is out of rc and if the oMLX side gets a cheaper prefix-cache path for its large system prompt; with this model its extra output was padding, not quality.

Reproduce: `~/local-ai/harness/bin/run-one.sh <pi|opencode|mini|dsh> <a-bugfix|b-feature> <n>`, aggregate with `bin/summary.py`; quality: `bin/blind.sh`, grade `blind/<task>/S*.patch` against `RUBRIC.md` into `grader<n>.json`, join with `bin/quality.py`. Card: `~/local-ai/harness/share/build.py`.
