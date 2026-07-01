#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Benchmark sui modelli GROSSI di NITRO (5070, remoto via tailnet) — quelli che sul 3060 non girano bene.
Stessi 13 task. Salva results_nitro_*.jsonl. Da giudicare poi con judge.py."""
import json,time,sys,os,datetime,urllib.request
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); from tasks import TASKS
NITRO="http://100.120.104.94:11434/api/generate"
MODELS=[
 ("gemma4:26b","Gemma4 26B @NITRO","heavy"),
 ("nemotron-cascade-2:latest","Nemotron-Cascade-2 24B @NITRO","heavy"),
 ("huihui_ai/qwen2.5-abliterate:14b-instruct-q4_K_M","Qwen2.5 14B abliterated @NITRO","light"),
 ("qwen2.5-coder:14b","Qwen2.5-Coder 14B @NITRO","light"),
]
def npf(c): return {'website':5000,'strategy':1200,'recipe':1200,'code':1200,'copy':400}.get(c,400)
def log(*a): print(f"[{datetime.datetime.now():%H:%M:%S}]",*a,flush=True)
ts=datetime.datetime.now().strftime('%Y%m%d_%H%M'); outp=f"results/results_nitro_{ts}.jsonl"
log(f"NITRO bench -> {outp}")
with open(outp,'a') as o:
  for name,lab,tier in MODELS:
    log(f"=== {lab} ===")
    for t in TASKS:
      wj=t['expects']=='json'; rec={'model':name,'model_lab':lab,'tier':tier,'mode':'nitro','task':t['id'],'cat':t['cat'],'expects':t['expects']}
      try:
        b={'model':name,'prompt':t['prompt'],'system':t.get('sys',''),'stream':False,'think':False,'keep_alive':'10m','options':{'temperature':0.2 if wj else 0.5,'num_predict':npf(t['cat'])}}
        if wj: b['format']='json'
        t0=time.time(); r=json.loads(urllib.request.urlopen(urllib.request.Request(NITRO,data=json.dumps(b).encode(),headers={'Content-Type':'application/json'}),timeout=600).read())
        resp=r.get('response',''); ev=r.get('eval_count') or 0; evd=(r.get('eval_duration') or 0)/1e9
        rec.update({'ok':True,'wall_s':round(time.time()-t0,1),'tok_s':round(ev/evd,2) if evd else 0,'check':t['check'](resp),'response':resp})
        log(f"  {t['id']:18s} {rec['tok_s']:5.1f}tk/s check={rec['check']['passed']}({rec['check']['score']})")
      except Exception as e: rec.update({'ok':False,'error':str(e)[:100]}); log(f"  {t['id']:18s} ERR {str(e)[:50]}")
      o.write(json.dumps(rec,ensure_ascii=False)+"\n"); o.flush()
log("NITRO BENCH FINITO")
