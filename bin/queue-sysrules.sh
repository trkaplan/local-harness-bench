#!/bin/bash
ROOT=$(cd "$(dirname "$0")/.." && pwd); export SYSRULES=$ROOT/tasks/RULES-coverage-v2.md
for h in pi mini opencode; do for n in s1 s2; do
  echo "$(date +%H:%M:%S) start $h $n"; $ROOT/bin/run-one.sh $h b-feature $n | tail -1 | cut -c1-200
done; done
$ROOT/bin/check-leftovers.sh --kill
echo "$(date +%H:%M:%S) ALL DONE"
