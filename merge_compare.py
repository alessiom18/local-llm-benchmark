#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Confronto: il modello FUSO vs i suoi 2 genitori, sugli stessi 13 task. Poi judge.py li giudica."""
import json, time, sys, os, datetime, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from tasks import TASKS
OLLAMA = "http://localhost:11434/api/generate"
MODELS = [
    {'name': 'qwen-dare:7b',     'lab': 'Qwen 7B DARE-TIES (4 fusi)',     'tier': 'light'},
    {'name': 'qwen-ties:7b',     'lab': 'Qwen 7B TIES (4 fusi)',          'tier': 'light'},
    {'name': 'qwen-merge:7b',    'lab': 'Qwen 7B SLERP (instruct+coder)', 'tier': 'light'},
    {'name': 'qwen-franken:11b', 'lab': 'Qwen 11B FRANKENMERGE',          'tier': 'light'},
    {'name': 'qwen2.5:7b',       'lab': 'Qwen2.5 7B Instruct (genitore)', 'tier': 'light'},
    {'name': 'qwen2.5-coder:7b', 'lab': 'Qwen2.5-Coder 7B (genitore)',    'tier': 'light'},
]
def npfor(cat):
    return {'website':5000,'strategy':1200,'recipe':1200,'code':1200,'copy':400}.get(cat,400)
def log(*a): print(f"[{datetime.datetime.now():%H:%M:%S}]", *a, flush=True)
def inst(n):
    try:
        r=urllib.request.urlopen("http://localhost:11434/api/tags",timeout=10)
        return n in {m['name'] for m in json.loads(r.read()).get('models',[])}
    except: return False
ts=datetime.datetime.now().strftime('%Y%m%d_%H%M'); outp=os.path.join(HERE,'results',f'results_mergecmp_{ts}.jsonl')
log(f"confronto fusione -> {outp}")
with open(outp,'a') as out:
    for m in MODELS:
        if not inst(m['name']): log("MANCA "+m['name']); continue
        log("=== "+m['lab']+" ===")
        for t in TASKS:
            wj=(t['expects']=='json'); np=npfor(t['cat'])
            rec={'model':m['name'],'model_lab':m['lab'],'tier':'light','mode':'mergecmp',
                 'task':t['id'],'cat':t['cat'],'expects':t['expects'],'ts':datetime.datetime.now().isoformat(timespec='seconds')}
            try:
                body={'model':m['name'],'prompt':t['prompt'],'system':t.get('sys',''),'stream':False,
                      'think':False,'keep_alive':'15m','options':{'temperature':0.2 if wj else 0.5,'num_predict':np}}
                if wj: body['format']='json'
                t0=time.time()
                r=urllib.request.urlopen(urllib.request.Request(OLLAMA,data=json.dumps(body).encode(),
                    headers={'Content-Type':'application/json'}),timeout=600)
                j=json.loads(r.read()); ev=j.get('eval_count') or 0; evd=(j.get('eval_duration') or 0)/1e9
                resp=j.get('response',''); chk=t['check'](resp)
                rec.update({'wall_s':round(time.time()-t0,1),'tokens':ev,'tok_s':round(ev/evd,2) if evd else 0,
                            'check':chk,'response':resp,'ok':True})
                log(f"  {t['id']:18s} {rec['tok_s']:5.1f}tk/s check={chk['passed']}({chk['score']})")
            except Exception as e:
                rec.update({'ok':False,'error':str(e)[:120]}); log(f"  {t['id']:18s} ERR {str(e)[:60]}")
            out.write(json.dumps(rec,ensure_ascii=False)+"\n"); out.flush()
        try: urllib.request.urlopen(urllib.request.Request(OLLAMA,data=json.dumps({'model':m['name'],'prompt':'ok','keep_alive':'0','stream':False}).encode(),headers={'Content-Type':'application/json'}),timeout=60)
        except: pass
log("CONFRONTO FINITO")
