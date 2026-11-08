#!/bin/bash
# re-run b-feature for pi/mini/opencode with the coverage rule appended to the prompt
ROOT=$(cd "$(dirname "$0")/.." && pwd); export RULES=$ROOT/tasks/RULES-coverage.md
for h in pi mini opencode; do for n in r1 r2; do
  echo "$(date +%H:%M:%S) start $h $n"; $ROOT/bin/run-one.sh $h b-feature $n | tail -1
done; done
$ROOT/bin/check-leftovers.sh --kill
echo "$(date +%H:%M:%S) ALL DONE"
