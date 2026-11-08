#!/bin/bash
# run-one.sh <harness: pi|opencode|mini|dsh> <task: a-bugfix|b-feature> <run#>
# Copies the task fixture, runs the harness headless against oMLX, records time / tokens / LLM calls /
# external connections, then runs the hidden tests. Result: ~/local-ai/harness/runs/<h>-<task>-<n>/result.json
set -u
H=$1; TASK=$2; N=$3; ROOT=$(cd "$(dirname "$0")/.." && pwd); RUN=$ROOT/runs/$H-$TASK-$N; TIMEOUT=${TIMEOUT:-1800}
PY=$ROOT/tasks/.venv/bin/python; STATS=${OMLX_URL:-http://127.0.0.1:8018}/admin/api/stats; OLOG=${OMLX_LOG:-$HOME/local-ai/qwen-flash-next/logs/omlx.log}
/bin/rm -rf "$RUN"; mkdir -p "$RUN"; cp -R "$ROOT/tasks/$TASK/repo" "$RUN/repo"
[ -d "$RUN/repo/.git" ] || ( cd "$RUN/repo" && git init -q && git add -A && git -c user.name=bench -c user.email=bench@localhost commit -qm baseline )
PROMPT="$(cat "$ROOT/tasks/$TASK/TASK.md")

Work in the current directory. Use \`$PY -m pytest -q\` to run tests (pytest is in that interpreter)."
if [ -n "${RULES:-}" ]; then PROMPT="$PROMPT

$(cat "$RULES")"; fi
stats() { curl -s $STATS | $PY -I -c 'import json,sys;d=json.load(sys.stdin);print(d["total_requests"],d["total_prompt_tokens"],d["total_completion_tokens"])'; }
read R0 P0 C0 <<< "$(stats)"; L0=$(wc -l < "$OLOG"); T0=$(date +%s)
cd "$RUN/repo"
export OMLX_API_KEY=local
case $H in
  pi) export PI_CODING_AGENT_DIR=$ROOT/cfg/pi PI_OFFLINE=1 PI_SKIP_VERSION_CHECK=1 PI_TELEMETRY=0
      CMD=(node $ROOT/src/pi/packages/coding-agent/dist/bundle/cli.js --provider omlx --model qwen-flash-next --no-session ${SYSRULES:+--append-system-prompt "$SYSRULES"} --print "$PROMPT");;
  opencode) export OPENCODE_CONFIG_DIR=$ROOT/cfg/opencode${SYSRULES:+-sys} OPENCODE_DISABLE_AUTOUPDATE=1 DO_NOT_TRACK=1 OPENCODE_DISABLE_FREE_MODELS=1 OPENCODE_DISABLE_MODELS_FETCH=1 XDG_DATA_HOME=$ROOT/cfg/opencode/data XDG_CACHE_HOME=$ROOT/cfg/opencode/cache
      CMD=($ROOT/src/opencode/packages/cli/dist/cli-darwin-arm64/bin/opencode run --model omlx/qwen-flash-next "$PROMPT");;
  mini) export MSWEA_CONFIGURED=1 MSWEA_MODEL_NAME=openai/qwen-flash-next MSWEA_COST_TRACKING=ignore_errors LITELLM_LOCAL_MODEL_COST_MAP=True LITELLM_TELEMETRY=False MSWEA_SILENT_STARTUP=1 MSWEA_GLOBAL_CONFIG_DIR=$ROOT/cfg/mini MSWEA_GLOBAL_CALL_LIMIT=150
      CMD=($ROOT/src/mini-swe-agent/.venv/bin/mini -c mini.yaml -c $ROOT/cfg/mini/mini-omlx.yaml ${SYSRULES:+-c $ROOT/cfg/mini/mini-sysrules.yaml} -y --exit-immediately -t "$PROMPT" -o "$RUN/traj.json");;
  dsh) export DSH_HOME=$ROOT/cfg/dsh DSH_TELEMETRY_DISABLED=1 DSH_TELEMETRY_MODE=DISABLED DSH_PERMISSION_MODE=workspace-write
      CMD=(node $ROOT/src/deepseek-harness/apps/cli/lib/bin.js --profile headless --approval-policy never "$PROMPT");;
  *) echo "unknown harness $H"; exit 2;;
esac
( "${CMD[@]}" > "$RUN/stdout.txt" 2> "$RUN/stderr.txt" < /dev/null & P=$!; echo $P > "$RUN/pid"
  ( sleep $TIMEOUT & SP=$!; echo $SP > "$RUN/sleeper"; wait $SP; kill -0 $P 2>/dev/null && { echo "TIMEOUT" >> "$RUN/stderr.txt"; pkill -P $P; kill $P; } ) >/dev/null 2>&1 & W=$!
  $ROOT/bin/netwatch.sh "$H-$TASK-$N" $P; wait $P; echo $? > "$RUN/exit"; kill $(cat "$RUN/sleeper" 2>/dev/null) $W 2>/dev/null )
[ "$H" = opencode ] && pkill -f "opencode serve --service" 2>/dev/null
T1=$(date +%s); read R1 P1 C1 <<< "$(stats)"; L1=$(wc -l < "$OLOG")
sed -n "$((L0+1)),${L1}p" "$OLOG" | grep "Chat completion" > "$RUN/omlx-requests.log"
LENGTH=$(grep -c "finish_reason=length" "$RUN/omlx-requests.log")
# hidden tests (copied in, then removed so the diff stays clean)
cp "$ROOT/tasks/$TASK/hidden/test_hidden.py" tests/test_hidden.py
$PY -m pytest -q tests/test_hidden.py > "$RUN/hidden.txt" 2>&1; HID=$?
HIDSUM=$(tail -1 "$RUN/hidden.txt")
/bin/rm -f tests/test_hidden.py
$PY -m pytest -q > "$RUN/visible.txt" 2>&1; VIS=$?; VISSUM=$(tail -1 "$RUN/visible.txt")
git add -A >/dev/null 2>&1; git diff --cached --stat -- . ':!**/__pycache__/**' ':!**/.pytest_cache/**' > "$RUN/diffstat.txt"; git diff --cached -- . ':!**/__pycache__/**' ':!**/.pytest_cache/**' > "$RUN/diff.patch"; git reset -q >/dev/null 2>&1
NET=$(wc -l < "$ROOT/runs/net-$H-$TASK-$N.log" | tr -d ' ')
cat > "$RUN/result.json" <<J
{"harness":"$H","task":"$TASK","run":"$N","exit":$(cat "$RUN/exit"),"wall_s":$((T1-T0)),"llm_calls":$((R1-R0)),"prompt_tokens":$((P1-P0)),"completion_tokens":$((C1-C0)),"length_finishes":$LENGTH,"hidden_pass":$([ $HID = 0 ] && echo true || echo false),"hidden_summary":"$HIDSUM","visible_pass":$([ $VIS = 0 ] && echo true || echo false),"visible_summary":"$VISSUM","external_conns":$NET,"started":"$(date -r $T0 +%FT%T)"}
J
cat "$RUN/result.json"
