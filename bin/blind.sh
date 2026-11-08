#!/usr/bin/env bash
# Build blinded review packets: blind/<task>/S<nn>.patch + KEY.json
set -euo pipefail
cd "$(dirname "$0")/.."
rm -rf blind; mkdir -p blind
for task in a-bugfix b-feature; do
  mkdir -p "blind/$task"
  runs=$(ls -d runs/*-$task-[0-9] | sort -R)
  i=0; echo "{" > "blind/$task/KEY.json"
  for r in $runs; do
    i=$((i+1)); id=$(printf "S%02d" $i)
    # strip anything that could leak the harness: only the patch itself is shared, with harness-specific
    # paths (none expected in repo diffs) scrubbed defensively
    sed -E 's#(deepseek[-_]?harness|opencode|mini-swe-agent|\bdsh\b|\bpi\b)#HARNESS#gI' "$r/diff.patch" > "blind/$task/$id.patch"
    printf '  "%s": "%s",\n' "$id" "$(basename $r)" >> "blind/$task/KEY.json"
  done
  sed -i '' '$ s/,$//' "blind/$task/KEY.json"; echo "}" >> "blind/$task/KEY.json"
  cp "tasks/$task/TASK.md" "blind/$task/TASK.md"
done
echo "packets:"; find blind -name '*.patch' | sort | xargs wc -l | tail -1
