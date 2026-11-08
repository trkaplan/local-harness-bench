#!/usr/bin/env python3
"""Render the benchmark card in TR and EN. Usage: build.py  (writes bench-card-{tr,en}.html + PNGs)"""
import subprocess, os
CHROME=os.path.expanduser("~/Library/Caches/ms-playwright/chromium_headless_shell-1248/chrome-headless-shell-mac-arm64/chrome-headless-shell")
H=["Pi","mini-swe-agent","opencode","deepseek-harness"]
WALL={"A":[28,42,40,123],"B":[66,61,86,209]}
TOK={"A":[29,42,102,302],"B":[89,58,237,580]}
QUAL={"A":[9.2,9.8,9.5,9.2],"B":[10.0,10.0,10.5,6.2]}
LINES={"A":[54,50,54,80],"B":[225,237,263,433]}
T={
"tr":dict(title="Hangi kodlama harness'ı lokal Qwen'i en iyi sürüyor?",sub="Qwen3.8-Flash-Next · M5 Max 128 GB · ~78 tok/s",
 p1="Süre",u1="saniye, görev başına",p2="Prompt token",u2="bin token, görev başına",p3="Diff boyutu",u3="eklenen satır, görev başına",p4="Kod kalitesi",u4="12 üzerinden, kör inceleme, 6 kriter",
 lA="Bug fix (70 satır modül, 7 gizli test)",lB="Feature (SQLite backend + migrate + rename, 11 gizli test)",
 foot="Pi v1.5.0 · opencode v2.2.6 · mini-swe-agent v2.4.6 · deepseek-harness 0.2.2-rc.1 · kaynaktan derlendi, telemetri kapalı · kalite: 2 bağımsız kör puanlayıcı, rubric: sağlamlık, test kapsamı, test kalitesi, doküman, spec'e sadakat, tutarlılık",
 b1="⚡ EN HIZLI",b2="💰 EN VERİMLİ"),
"en":dict(title="Which coding-agent harness drives a local Qwen best?",sub="Qwen3.8-Flash-Next · M5 Max 128 GB · ~78 tok/s",
 p1="Wall time",u1="seconds per task",p2="Prompt tokens",u2="thousand tokens per task",p3="Diff size",u3="lines added per task",p4="Code quality",u4="out of 12, blind review, 6 criteria",
 lA="Bug fix (70-line module, 7 hidden tests)",lB="Feature (SQLite backend + migrate + rename, 11 hidden tests)",
 foot="Pi v1.5.0 · opencode v2.2.6 · mini-swe-agent v2.4.6 · deepseek-harness 0.2.2-rc.1 · built from source, telemetry off · quality: 2 independent blind graders, rubric: robustness, spec coverage, test quality, docs, spec fidelity, consistency",
 b1="⚡ FASTEST",b2="💰 BEST VALUE"),
}
TPL='''<!doctype html><html><head><meta charset="utf-8"><style>
:root{--surface:#1a1a19;--t1:#f0efec;--t2:#c3c2b7;--t3:#8a897f;--grid:#33332f;--s1:#3987e5;--s2:#d95926}
*{box-sizing:border-box;margin:0}
body{width:1600px;height:900px;background:var(--surface);color:var(--t1);font-family:-apple-system,"SF Pro Display",Inter,Helvetica,Arial,sans-serif;padding:56px 64px;display:flex;flex-direction:column}
h1{font-size:40px;font-weight:700;letter-spacing:-.5px}
.sub{color:var(--t2);font-size:21px;margin-top:10px}
.charts{display:flex;gap:30px;flex:1;margin-top:40px}
.chart{flex:1;display:flex;flex-direction:column}
.chart h2{font-size:21px;font-weight:600}
.chart .unit{font-size:15px;color:var(--t3);margin-top:3px}
svg{width:100%%;flex:1;margin-top:10px}
.legend{display:flex;gap:28px;font-size:16px;color:var(--t2)}
.legend i{display:inline-block;width:12px;height:12px;border-radius:3px;margin-right:8px;vertical-align:-1px}
.foot{display:flex;justify-content:space-between;gap:40px;color:var(--t3);font-size:14px;margin-top:8px;line-height:1.35}
text{font-family:inherit}
</style></head><body>
<h1>%(title)s</h1><div class="sub">%(sub)s</div>
<div class="charts">
<div class="chart"><h2>%(p1)s</h2><div class="unit">%(u1)s</div><svg id="c1" viewBox="0 0 345 520" preserveAspectRatio="xMinYMin meet"></svg></div>
<div class="chart"><h2>%(p2)s</h2><div class="unit">%(u2)s</div><svg id="c2" viewBox="0 0 345 520" preserveAspectRatio="xMinYMin meet"></svg></div>
<div class="chart"><h2>%(p3)s</h2><div class="unit">%(u3)s</div><svg id="c3" viewBox="0 0 345 520" preserveAspectRatio="xMinYMin meet"></svg></div>
<div class="chart"><h2>%(p4)s</h2><div class="unit">%(u4)s</div><svg id="c4" viewBox="0 0 345 520" preserveAspectRatio="xMinYMin meet"></svg></div>
</div>
<div class="legend"><span><i style="background:var(--s1)"></i>%(lA)s</span><span><i style="background:var(--s2)"></i>%(lB)s</span></div>
<div class="foot"><span>%(foot)s</span><span style="white-space:nowrap">2026-11-08</span></div>
<script>
const H=%(H)s;
const data={c1:{A:%(wA)s,B:%(wB)s,fmt:v=>v+" s",max:null,badge:{row:0,text:"%(b1)s"}},
            c2:{A:%(tA)s,B:%(tB)s,fmt:v=>v+"K",max:null,badge:{row:1,text:"%(b2)s"}},
            c3:{A:%(lA_)s,B:%(lB_)s,fmt:v=>v,max:null,badge:null},
            c4:{A:%(qA)s,B:%(qB)s,fmt:v=>v.toFixed(1),max:12,badge:null}};
const css=getComputedStyle(document.documentElement),c=k=>css.getPropertyValue(k);
function draw(id){const d=data[id],svg=document.getElementById(id);const W=345,L=96,R=52,T=10,rowH=125,bh=40,gap=2;
const max=d.max||Math.max(...d.A,...d.B)*1.08;const x=v=>L+(W-L-R)*v/max;let s="";
for(let i=0;i<=4;i++){const px=x(max/4*i);s+=`<line x1="${px}" y1="${T}" x2="${px}" y2="${T+rowH*4}" stroke="${c('--grid')}"/>`;}
H.forEach((h,i)=>{const y=T+rowH*i+18;const lbl=["Pi","mini","opencode","dsh"][i];
s+=`<text x="${L-14}" y="${y+bh+gap/2+5}" text-anchor="end" font-size="17" fill="${c('--t1')}" font-weight="600">${lbl}</text>`;
if(d.badge&&d.badge.row===i){s+=`<text x="${L-14}" y="${y+bh+gap/2+28}" text-anchor="end" font-size="11.5" fill="${c('--s1')}" font-weight="700">${d.badge.text}</text>`;}
[["A","--s1",0],["B","--s2",bh+gap]].forEach(([k,col,off])=>{const v=d[k][i],w=x(v)-L,yy=y+off;
s+=`<path d="M${L},${yy} H${L+w-4} a4,4 0 0 1 4,4 v${bh-8} a4,4 0 0 1 -4,4 H${L} Z" fill="${c(col)}"/>`;
s+=`<text x="${L+w+9}" y="${yy+bh/2+6}" font-size="15" fill="${c('--t2')}">${d.fmt(v)}</text>`;});});
s+=`<line x1="${L}" y1="${T}" x2="${L}" y2="${T+rowH*4}" stroke="${c('--t3')}"/>`;svg.innerHTML=s;}
draw("c1");draw("c2");draw("c3");draw("c4");
</script></body></html>
'''
for lang,t in T.items():
    html=TPL%dict(t,H=H,wA=WALL["A"],wB=WALL["B"],tA=TOK["A"],tB=TOK["B"],qA=QUAL["A"],qB=QUAL["B"],lA_=LINES["A"],lB_=LINES["B"])
    open(f"bench-card-{lang}.html","w").write(html)
    out=os.path.abspath(f"harness-bench-2026-11-08-{lang}.png")
    subprocess.run([CHROME,"--headless","--no-sandbox","--hide-scrollbars","--force-device-scale-factor=2","--window-size=1600,900",f"--screenshot={out}",f"file://{os.path.abspath(f'bench-card-{lang}.html')}"],stderr=subprocess.DEVNULL,check=True)
    print(out)
