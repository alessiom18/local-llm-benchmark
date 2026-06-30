#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Orchestratore: open-clean → varianti → giudice(gemma31) → il VINCITORE rigiudica (riprova) → report."""
import subprocess, glob, os, json, sys, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
def log(*a): print(f"[{datetime.datetime.now():%H:%M:%S}]", *a, flush=True)
PY = '/usr/bin/python3'
LAB2NAME = {
 'Qwen2.5 3B (default)':'qwen2.5:3b','Cogito 8B':'cogito:8b','Gemma4 12B':'gemma4:12b',
 'Qwen2.5-Coder 14B':'qwen2.5-coder:14b','DeepSeek-Coder-V2 16B':'deepseek-coder-v2:16b',
 'Gemma4 31B':'gemma4:31b','Qwen3.6 35B (MoE)':'qwen3.6:35b',
 'Qwen2.5-Coder 32B abliterated':'hf.co/bartowski/Qwen2.5-Coder-32B-Instruct-abliterated-GGUF:Q4_K_M',
 'Llama-3.3 70B abliterated':'hf.co/mradermacher/Llama-3.3-70B-Instruct-abliterated-GGUF:Q3_K_M'}
def latest(pat, excl=()):
    fs=[f for f in glob.glob(os.path.join(HERE,'results',pat)) if not any(e in f for e in excl)]
    return max(fs,key=os.path.getmtime) if fs else None
def rd(p): return [json.loads(l) for l in open(p,encoding='utf-8') if l.strip()] if p and os.path.exists(p) else []

# 1) OPEN puliti
log("STEP 1: open-clean"); subprocess.run([PY,'run_open_clean.py','--until','12:30'],cwd=HERE)
# 2) VARIANTI
log("STEP 2: varianti"); subprocess.run([PY,'run_variants.py','--until','13:40'],cwd=HERE)
# 3) MERGE: oggettivi dal RUN1 + aperti dal clean
run1=latest('results_*.jsonl',excl=('variants','open','sites','merged'))
openf=latest('results_open_*.jsonl')
log(f"STEP 3: merge run1={os.path.basename(run1) if run1 else None} open={os.path.basename(openf) if openf else None}")
OPEN={'strategy','recipe','code','copy','website'}
merged=[r for r in rd(run1) if r.get('cat') not in OPEN]      # oggettivi
merged+=[r for r in rd(openf) if r.get('cat') in OPEN]         # aperti puliti
ts=datetime.datetime.now().strftime('%Y%m%d_%H%M')
mf=os.path.join(HERE,'results',f'results_merged_{ts}.jsonl')
open(mf,'w').write("\n".join(json.dumps(r,ensure_ascii=False) for r in merged))
log(f"   merged {len(merged)} record → {os.path.basename(mf)}")
# 4) GIUDICE gemma31
log("STEP 4: giudice gemma4:31b"); subprocess.run([PY,'judge.py',mf,'--judge','gemma4:31b'],cwd=HERE)
rk=json.load(open(os.path.join(HERE,'report','ranking_gemma4_31b.json')))
winner=rk[0]['lab']; log(f"   VINCITORE (giudice gemma31): {winner} ({rk[0]['score']})")
# 5) il VINCITORE rigiudica (riprova). Se vincitore==gemma31, usa il 2º come contro-giudice.
wlab = winner if winner!='Gemma4 31B' else rk[1]['lab']
wname = LAB2NAME.get(wlab)
if wname and '70B' not in wlab:
    log(f"STEP 5: contro-giudice = {wlab} ({wname})")
    subprocess.run([PY,'judge.py',mf,'--judge',wname],cwd=HERE)
else:
    log(f"STEP 5: salto contro-giudice ({wlab} troppo lento o assente)")
log("MASTER FINITO.")
