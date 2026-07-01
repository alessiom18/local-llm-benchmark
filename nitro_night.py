#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Programma NOTTURNO di NITRO (5070, remoto) — gira su MARCO ma TUTTA l'inferenza è su NITRO via tailnet.
Scarica nuove famiglie su NITRO, le benchmarka sui 13 task. Deadline 06:45. MARCO resta libero per la sua notte."""
import json, time, sys, os, datetime, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tasks import TASKS
B = "http://100.120.104.94:11434"
DEADLINE = datetime.datetime.now().replace(hour=6, minute=45, second=0, microsecond=0)
if DEADLINE <= datetime.datetime.now():
    DEADLINE += datetime.timedelta(days=1)

def log(*a): print(f"[{datetime.datetime.now():%H:%M:%S}]", *a, flush=True)
def over(): return datetime.datetime.now() >= DEADLINE
# Pause di RAFFREDDAMENTO (fa caldo): la GPU respira tra i carichi.
COOLDOWN_TASK = int(os.environ.get('NITRO_COOL_TASK', '12'))    # pausa breve dopo OGNI task
COOLDOWN_MODEL = int(os.environ.get('NITRO_COOL_MODEL', '120'))  # pausa lunga tra un MODELLO e l'altro (VRAM scarica = si raffredda)
def cool(sec):
    end = time.time() + sec
    while time.time() < end and not over():
        time.sleep(min(5, end - time.time()))

PULL = ["mistral-nemo:latest", "llama3.1:8b", "gemma2:9b", "phi4:latest", "deepseek-r1:14b"]
TARGET = [
    ("gemma4:26b", "Gemma4 26B", "heavy"),
    ("nemotron-cascade-2:latest", "Nemotron-Cascade2 24B", "heavy"),
    ("huihui_ai/qwen2.5-abliterate:14b-instruct-q4_K_M", "Qwen2.5 14B abliterated", "light"),
    ("qwen2.5-coder:14b", "Qwen2.5-Coder 14B", "light"),
    ("mistral-nemo:latest", "Mistral-Nemo 12B", "light"),
    ("llama3.1:8b", "Llama3.1 8B", "light"),
    ("gemma2:9b", "Gemma2 9B", "light"),
    ("phi4:latest", "Phi-4 14B", "light"),
    ("deepseek-r1:14b", "DeepSeek-R1 14B", "heavy"),
]

def tags():
    try:
        return {m['name'] for m in json.loads(urllib.request.urlopen(B + "/api/tags", timeout=15).read())["models"]}
    except Exception:
        return set()

def gen(payload, timeout=600):
    return json.loads(urllib.request.urlopen(urllib.request.Request(
        B + "/api/generate", data=json.dumps(payload).encode(),
        headers={'Content-Type': 'application/json'}), timeout=timeout).read())

def pull(name):
    log("pull", name)
    try:
        r = urllib.request.urlopen(urllib.request.Request(
            B + "/api/pull", data=json.dumps({"name": name, "stream": False}).encode(),
            headers={'Content-Type': 'application/json'}), timeout=3600)
        r.read(); log("  ok", name)
    except Exception as e:
        log("  pull fail", name, str(e)[:60])

def npf(c): return {'website': 5000, 'strategy': 1200, 'recipe': 1200, 'code': 1200, 'copy': 400}.get(c, 400)

ts = datetime.datetime.now().strftime('%Y%m%d_%H%M')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results', f'results_nitro_{ts}.jsonl')
log(f"NITRO night start (deadline {DEADLINE:%H:%M}) -> {OUT}")

present = tags()
for m in PULL:
    if over(): break
    if not any(m.split(':')[0] in h for h in present):
        pull(m)

with open(OUT, 'a') as o:
    for name, lab, tier in TARGET:
        if over(): log("deadline"); break
        present = tags()
        if name not in present and not any(name.split(':')[0] in h for h in present):
            log("salto (assente)", name); continue
        log(f"=== {lab} ===")
        for t in TASKS:
            if over(): break
            wj = (t['expects'] == 'json')
            rec = {'model': name, 'model_lab': lab + " @NITRO", 'tier': tier, 'mode': 'nitro',
                   'task': t['id'], 'cat': t['cat'], 'expects': t['expects']}
            try:
                b = {'model': name, 'prompt': t['prompt'], 'system': t.get('sys', ''), 'stream': False,
                     'think': False, 'keep_alive': '8m', 'options': {'temperature': 0.2 if wj else 0.5, 'num_predict': npf(t['cat'])}}
                if wj: b['format'] = 'json'
                t0 = time.time(); r = gen(b)
                resp = r.get('response', ''); ev = r.get('eval_count') or 0; evd = (r.get('eval_duration') or 0) / 1e9
                rec.update({'ok': True, 'wall_s': round(time.time() - t0, 1), 'tok_s': round(ev / evd, 2) if evd else 0,
                            'check': t['check'](resp), 'response': resp})
                log(f"  {t['id']:16s} {rec['tok_s']:5.1f}tk/s {rec['check']['passed']}")
            except Exception as e:
                rec.update({'ok': False, 'error': str(e)[:80]}); log(f"  {t['id']:16s} ERR {str(e)[:40]}")
            o.write(json.dumps(rec, ensure_ascii=False) + "\n"); o.flush()
            cool(COOLDOWN_TASK)   # ❄️ pausa breve tra i task
        try: gen({"model": name, "prompt": "ok", "keep_alive": "0", "stream": False}, 60)  # scarica dalla VRAM
        except Exception: pass
        log(f"  ❄️ raffreddamento {COOLDOWN_MODEL}s (GPU scarica)")
        cool(COOLDOWN_MODEL)   # ❄️ pausa lunga tra i modelli
log("NITRO NIGHT FINITO -> " + OUT)
