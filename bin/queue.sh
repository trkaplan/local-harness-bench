#!/bin/bash
ROOT=$(cd "$(dirname "$0")/.." && pwd)
# queue.sh : runs the listed (harness task run) triples sequentially; log in runs/queue.log
cd ~/local-ai/harness
while read -r h t n; do
  [ -z "$h" ] && continue
  [ -f "runs/$h-$t-$n/result.json" ] && { echo "skip $h $t $n (done)"; continue; }
  echo "=== $(date +%T) start $h $t $n"
  TIMEOUT=${TIMEOUT:-1800} bin/run-one.sh "$h" "$t" "$n" | tail -1
done <<'LIST'
opencode a-bugfix 1
mini a-bugfix 1
dsh a-bugfix 1
pi b-feature 1
opencode b-feature 1
mini b-feature 1
dsh b-feature 1
pi a-bugfix 2
opencode a-bugfix 2
mini a-bugfix 2
dsh a-bugfix 2
pi b-feature 2
opencode b-feature 2
mini b-feature 2
dsh b-feature 2
LIST
$ROOT/bin/check-leftovers.sh --kill
echo "=== $(date +%T) queue done"
