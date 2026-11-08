#!/bin/bash
# netwatch.sh <label> <pid> : logs every non-loopback TCP/UDP connection of <pid> and its descendants until it exits.
# Output: ~/local-ai/harness/runs/net-<label>.log  (empty = no external traffic seen)
label=$1; pid=$2; out=~/local-ai/harness/runs/net-$label.log; : > "$out"
while kill -0 "$pid" 2>/dev/null; do
  pids="$pid"; frontier="$pid"
  for _ in 1 2 3 4; do
    kids=$(pgrep -P "${frontier//,/ -P }" 2>/dev/null | tr '\n' ' '); [ -z "$kids" ] && break
    pids="$pids,${kids// /,}"; pids=${pids%,}; frontier=${kids// /,}; frontier=${frontier%,}
  done
  ts=$(date +%H:%M:%S)
  lsof -nP -a -i -p "$pids" 2>/dev/null | awk -v ts="$ts" 'NR>1 && $9 !~ /127\.0\.0\.1|\[::1\]|localhost/ {print ts, $1, $2, $8, $9, $10}' >> "$out"
  sleep 0.3
done
sort -u -o "$out" "$out"
