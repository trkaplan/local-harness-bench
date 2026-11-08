#!/usr/bin/env bash
# After any benchmark run or experiment: make sure nothing we started is still alive.
# Lists (and with --kill, terminates) processes launched from this harness tree and their listening ports.
ROOT=$(cd "$(dirname "$0")/.." && pwd)
PIDS=$(pgrep -f "$ROOT/src/" || true)
if [ -z "$PIDS" ]; then echo "leftovers: none"; exit 0; fi
for p in $PIDS; do
  ps -o pid=,lstart=,command= -p "$p" | cut -c1-160
  lsof -nP -a -iTCP -sTCP:LISTEN -p "$p" 2>/dev/null | tail -n +2 | awk '{print "    listening:", $9}'
done
if [ "${1:-}" = "--kill" ]; then kill $PIDS 2>/dev/null; sleep 1; pkill -9 -f "$ROOT/src/" 2>/dev/null; echo "leftovers: killed"; else echo "leftovers: $(echo $PIDS | wc -w | tr -d ' ') process(es); run with --kill"; exit 1; fi
