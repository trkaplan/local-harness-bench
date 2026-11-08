#!/usr/bin/env python3
"""Aggregate runs/*/result.json into a markdown table."""
import json, glob, os, statistics as st
rows = [json.load(open(f)) for f in sorted(glob.glob(os.path.expanduser('~/local-ai/harness/runs/*/result.json')))]
print("| harness | task | run | wall s | LLM calls | prompt tok | compl tok | len cut | hidden | visible | ext conns | exit |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|")
for r in rows:
    print(f"| {r['harness']} | {r['task']} | {r['run']} | {r['wall_s']} | {r['llm_calls']} | {r['prompt_tokens']} | {r['completion_tokens']} | {r['length_finishes']} | {r['hidden_summary']} | {r['visible_summary']} | {r['external_conns']} | {r['exit']} |")
print()
print("| harness | task | runs | mean wall s | mean calls | mean prompt tok | hidden pass |")
print("|---|---|---|---|---|---|---|")
keys = sorted({(r['harness'], r['task']) for r in rows})
for h, t in keys:
    g = [r for r in rows if r['harness'] == h and r['task'] == t]
    print(f"| {h} | {t} | {len(g)} | {st.mean(r['wall_s'] for r in g):.0f} | {st.mean(r['llm_calls'] for r in g):.1f} | {st.mean(r['prompt_tokens'] for r in g):.0f} | {sum(r['hidden_pass'] for r in g)}/{len(g)} |")
