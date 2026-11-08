#!/usr/bin/env python3
"""Join blind grader scores with run metrics. Prints markdown + writes blind/quality.json."""
import json, glob, statistics as st
from pathlib import Path
root = Path(__file__).resolve().parent.parent
CRIT = ["robust", "spec-cov", "test-q", "docs", "fidelity", "consist"]
rows = []
for task in ["a-bugfix", "b-feature"]:
    key = json.load(open(root / "blind" / task / "KEY.json"))
    graders = [json.load(open(p)) for p in sorted(glob.glob(str(root / "blind" / task / "grader*.json")))]
    for sid, run in key.items():
        per = [g[sid]["scores"] for g in graders]
        mean = [st.mean(c) for c in zip(*per)]
        res = json.load(open(root / "runs" / run / "result.json"))
        h = run.split("-")[0]
        rows.append(dict(h=h, task=task, run=run, sid=sid, scores=mean, total=sum(mean),
                         totals=[sum(p) for p in per], wall=res["wall_s"], calls=res["llm_calls"],
                         ptok=res["prompt_tokens"], ctok=res["completion_tokens"]))
json.dump(rows, open(root / "blind" / "quality.json", "w"), indent=1)
print("| harness | task | run | " + " | ".join(CRIT) + " | total (g1/g2) |")
print("|" + "---|" * (len(CRIT) + 4))
for r in sorted(rows, key=lambda r: (r["h"], r["task"], r["run"])):
    print(f"| {r['h']} | {r['task']} | {r['sid']} | " + " | ".join(f"{s:g}" for s in r["scores"]) +
          f" | {r['total']:g} ({'/'.join(str(t) for t in r['totals'])}) |")
print("\n| harness | task | quality /12 | wall s | prompt tok | quality per 100K tok | quality per min |")
print("|---|---|---|---|---|---|---|")
agg = {}
for h in ["pi", "mini", "opencode", "dsh"]:
    for task in ["a-bugfix", "b-feature"]:
        rs = [r for r in rows if r["h"] == h and r["task"] == task]
        q = st.mean(r["total"] for r in rs); w = st.mean(r["wall"] for r in rs); p = st.mean(r["ptok"] for r in rs)
        agg[(h, task)] = dict(q=q, wall=w, ptok=p)
        print(f"| {h} | {task} | {q:.1f} | {w:.0f} | {p:,.0f} | {q / (p / 1e5):.1f} | {q / (w / 60):.1f} |")
print("\n| harness | quality /12 (both tasks) | per 100K tok | per min |")
print("|---|---|---|---|")
for h in ["pi", "mini", "opencode", "dsh"]:
    a, b = agg[(h, "a-bugfix")], agg[(h, "b-feature")]
    q = (a["q"] + b["q"]) / 2; p = (a["ptok"] + b["ptok"]) / 2; w = (a["wall"] + b["wall"]) / 2
    print(f"| {h} | {q:.1f} | {q / (p / 1e5):.1f} | {q / (w / 60):.1f} |")
