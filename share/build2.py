#!/usr/bin/env python3
"""Transposed card: one row per metric, harnesses as columns, vertical bars."""
import subprocess, os
CHROME=os.path.expanduser("~/Library/Caches/ms-playwright/chromium_headless_shell-1248/chrome-headless-shell-mac-arm64/chrome-headless-shell")
H=["Pi","mini-swe-agent","opencode","deepseek-harness"]
M={"time":{"A":[28,42,40,123],"B":[66,61,86,209]},
   "tok":{"A":[29,42,102,302],"B":[89,58,237,580]},
   "lines":{"A":[54,50,54,80],"B":[225,237,263,433]},
   "qual":{"A":[9.2,9.8,9.5,9.2],"B":[10.0,10.0,10.5,6.2]}}
T={"tr":dict(title="Hangi kodlama harness'ı lokal Qwen'i en iyi sürüyor?",sub="Qwen3.8-Flash-Next · M5 Max 128 GB · ~78 tok/s",
  rows=[("Süre","saniye"),("Prompt token","bin"),("Diff boyutu","eklenen satır"),("Kod kalitesi","12 üzerinden, kör inceleme")],
  lA="Bug fix (7 test)",lB="Feature: SQLite backend + migrate + rename (11 test)",
  foot="Pi v1.5.0 · opencode v2.2.6 · mini-swe-agent v2.4.6 · deepseek-harness 0.2.2-rc.1 · kaynaktan derlendi, telemetri kapalı · kalite: 2 bağımsız kör Claude puanlayıcı; rubric: sağlamlık, test kapsamı, test kalitesi, doküman, spec'e sadakat, tutarlılık",
  b1="⚡ EN HIZLI",b2="💰 EN VERİMLİ"),
 "en":dict(title="Which coding-agent harness drives a local Qwen best?",sub="Qwen3.8-Flash-Next · M5 Max 128 GB · ~78 tok/s",
  rows=[("Time","seconds"),("Prompt tokens","thousands"),("Diff size","lines added"),("Code quality","out of 12, blind review")],
  lA="Bug fix (7 tests)",lB="Feature: SQLite backend + migrate + rename (11 tests)",
  foot="Pi v1.5.0 · opencode v2.2.6 · mini-swe-agent v2.4.6 · deepseek-harness 0.2.2-rc.1 · built from source, telemetry off · quality: 2 independent blind Claude graders; rubric: robustness, spec coverage, test quality, docs, spec fidelity, consistency",
  b1="⚡ FASTEST",b2="💰 BEST VALUE")}
TPL='''<!doctype html><html><head><meta charset="utf-8"><style>
:root{--surface:#1a1a19;--t1:#f0efec;--t2:#c3c2b7;--t3:#8a897f;--grid:#33332f;--s1:#3987e5;--s2:#d95926}
*{box-sizing:border-box;margin:0}
body{width:1600px;height:900px;background:var(--surface);color:var(--t1);font-family:-apple-system,"SF Pro Display",Inter,Helvetica,Arial,sans-serif;padding:52px 64px 44px;display:flex;flex-direction:column}
h1{font-size:40px;font-weight:700;letter-spacing:-.5px}
.sub{color:var(--t2);font-size:21px;margin-top:8px}
svg{width:100%%;flex:1;margin-top:22px}
.legend{display:flex;gap:28px;font-size:16px;color:var(--t2)}
.legend i{display:inline-block;width:12px;height:12px;border-radius:3px;margin-right:8px;vertical-align:-1px}
.foot{display:flex;justify-content:space-between;gap:40px;color:var(--t3);font-size:14px;margin-top:8px;line-height:1.35}
text{font-family:inherit}
</style></head><body>
<h1>%(title)s</h1><div class="sub">%(sub)s</div>
<svg id="g" viewBox="0 0 1472 660" preserveAspectRatio="xMinYMin meet"></svg>
<div class="legend"><span><i style="background:var(--s1)"></i>%(lA)s</span><span><i style="background:var(--s2)"></i>%(lB)s</span></div>
<div class="foot"><span>%(foot)s</span><span style="white-space:nowrap">2026-11-08</span></div>
<script>
const H=%(H)s, M=%(M)s, ROWS=%(rows)s, badges={0:[0,"%(b1)s"],1:[1,"%(b2)s"]};
const keys=["time","tok","lines","qual"], fmt=[v=>v+" s",v=>v+"K",v=>v,v=>v.toFixed(1)];
const css=getComputedStyle(document.documentElement),c=k=>css.getPropertyValue(k);
const W=1472,PLOTW=1000,X0=0,TOP=44,ROWH=150,COLW=PLOTW/4,BW=54,GAP=2,HEAD=40,BASE=10;
let s="";
keys.forEach((k,r)=>{const d=M[k];const y0=TOP+r*ROWH, plotH=ROWH-HEAD-BASE-26, base=y0+HEAD+plotH;
 const max=k==="qual"?12.3:Math.max(...d.A,...d.B)*1.02;
 s+=`<text x="${X0}" y="${y0+16}" font-size="19" font-weight="600" fill="${c('--t1')}">${ROWS[r][0]} <tspan font-size="14" font-weight="400" fill="${c('--t3')}">· ${ROWS[r][1]}</tspan></text>`;
 s+=`<line x1="${X0}" y1="${base}" x2="${X0+PLOTW}" y2="${base}" stroke="${c('--grid')}"/>`;
 H.forEach((h,i)=>{const cx=X0+COLW*i+COLW/2;
  [["A","--s1",-BW-GAP/2],["B","--s2",GAP/2]].forEach(([t,col,off])=>{const v=d[t][i],hh=Math.max(3,plotH*v/max),x=cx+off,y=base-hh;
   s+=`<path d="M${x},${base} V${y+4} a4,4 0 0 1 4,-4 H${x+BW-4} a4,4 0 0 1 4,4 V${base} Z" fill="${c(col)}"/>`;
   s+=`<text x="${x+BW/2}" y="${y-7}" text-anchor="middle" font-size="15" fill="${c('--t2')}">${fmt[r](v)}</text>`;});
  if(r===0){s+=`<text x="${cx}" y="22" text-anchor="middle" font-size="20" font-weight="700" fill="${c('--t1')}">${h}</text>`;}
  if(badges[r]&&badges[r][0]===i){s+=`<text x="${cx}" y="${base+21}" text-anchor="middle" font-size="12.5" font-weight="700" fill="${c('--s1')}">${badges[r][1]}</text>`;}
 });});
document.getElementById("g").innerHTML=s;
</script></body></html>'''
import json
for lang,t in T.items():
    html=TPL%dict(t,H=json.dumps(H),M=json.dumps(M),rows=json.dumps(t["rows"]))
    open(f"bench-card2-{lang}.html","w").write(html)
    out=os.path.abspath(f"harness-bench-2026-11-08-{lang}-v2.png")
    subprocess.run([CHROME,"--headless","--no-sandbox","--hide-scrollbars","--force-device-scale-factor=2","--window-size=1600,900",f"--screenshot={out}",f"file://{os.path.abspath(f'bench-card2-{lang}.html')}"],stderr=subprocess.DEVNULL,check=True)
    print(out)
