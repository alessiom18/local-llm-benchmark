#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Re-run PULITO di TUTTI i task APERTI con num_predict ALTO (no troncamento) → giudizio EQUO.
Nel RUN 1, 36 risposte aperte erano troncate al tetto token (400-500) → penalizzate ingiustamente dal giudice.
Qui ogni task aperto ha token abbondanti. I task OGGETTIVI (JSON) restano dal RUN 1 (erano corti, non troncati).
Output: results/results_open_<ts>.jsonl. Deadline-aware.
"""
import json, time, sys, os, datetime, urllib.request, argparse
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from tasks import TASKS
OLLAMA = "http://localhost:11434/api/generate"
OPEN = {'strategy', 'recipe', 'code', 'copy', 'website'}
TASKS_OPEN = [t for t in TASKS if t['cat'] in OPEN]

def npfor(cat, heavy, name):
    if cat == 'website':
        return 3000 if '70B' in name else (4000 if heavy else 5000)
    if cat in ('strategy', 'recipe', 'code'):
        return 1200
    if cat == 'copy':
        return 400
    return 800

MODELS = [
    {'name': 'qwen2.5:3b', 'lab': 'Qwen2.5 3B (default)', 'tier': 'light', 'to': 600},
    {'name': 'cogito:8b', 'lab': 'Cogito 8B', 'tier': 'light', 'to': 600},
    {'name': 'gemma4:12b', 'lab': 'Gemma4 12B', 'tier': 'light', 'to': 900},
    {'name': 'qwen2.5-coder:14b', 'lab': 'Qwen2.5-Coder 14B', 'tier': 'light', 'to': 900},
    {'name': 'deepseek-coder-v2:16b', 'lab': 'DeepSeek-Coder-V2 16B', 'tier': 'light', 'to': 900},
    {'name': 'gemma4:31b', 'lab': 'Gemma4 31B', 'tier': 'heavy', 'to': 2400},
    {'name': 'qwen3.6:35b', 'lab': 'Qwen3.6 35B (MoE)', 'tier': 'heavy', 'to': 2400},
    {'name': 'hf.co/bartowski/Qwen2.5-Coder-32B-Instruct-abliterated-GGUF:Q4_K_M', 'lab': 'Qwen2.5-Coder 32B abliterated', 'tier': 'heavy', 'to': 2400},
    {'name': 'hf.co/mradermacher/Llama-3.3-70B-Instruct-abliterated-GGUF:Q3_K_M', 'lab': 'Llama-3.3 70B abliterated', 'tier': 'heavy', 'to': 3000},
]

def log(*a): print(f"[{datetime.datetime.now():%H:%M:%S}]", *a, flush=True)
def installed(n):
    try:
        r = urllib.request.urlopen("http://localhost:11434/api/tags", timeout=10)
        return n in {m['name'] for m in json.loads(r.read()).get('models', [])}
    except Exception: return False

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--until', default='13:30'); a = ap.parse_args()
    hh, mm = map(int, a.until.split(':')); now = datetime.datetime.now()
    dl = now.replace(hour=hh, minute=mm, second=0, microsecond=0)
    if dl <= now: dl += datetime.timedelta(days=1)
    ts = f"{now:%Y%m%d_%H%M}"; outp = os.path.join(HERE, 'results', f'results_open_{ts}.jsonl')
    log(f"open puliti → {outp} (deadline {dl:%H:%M}) · {len(TASKS_OPEN)} task aperti")
    with open(outp, 'a') as out:
        for m in MODELS:
            if datetime.datetime.now() >= dl: log("deadline"); break
            if not installed(m['name']): log("skip " + m['lab']); continue
            log(f"=== {m['lab']} ===")
            for t in TASKS_OPEN:
                if datetime.datetime.now() >= dl: break
                np = npfor(t['cat'], m['tier'] == 'heavy', m['lab'])
                rec = {'model': m['name'], 'model_lab': m['lab'], 'tier': m['tier'], 'mode': 'clean',
                       'task': t['id'], 'cat': t['cat'], 'expects': t['expects'], 'np': np,
                       'ts': datetime.datetime.now().isoformat(timespec='seconds')}
                try:
                    body = {'model': m['name'], 'prompt': t['prompt'], 'system': t.get('sys', ''),
                            'stream': False, 'think': False, 'keep_alive': '20m',
                            'options': {'temperature': 0.5, 'num_predict': np}}
                    t0 = time.time()
                    r = urllib.request.urlopen(urllib.request.Request(
                        OLLAMA, data=json.dumps(body).encode(), headers={'Content-Type': 'application/json'}), timeout=m['to'])
                    j = json.loads(r.read()); wall = round(time.time()-t0, 1)
                    ev = j.get('eval_count') or 0; evd = (j.get('eval_duration') or 0)/1e9
                    resp = j.get('response', ''); chk = t['check'](resp)
                    rec.update({'wall_s': wall, 'tokens': ev, 'tok_s': round(ev/evd, 2) if evd else 0,
                                'check': chk, 'response': resp, 'ok': True, 'truncated': ev >= np*0.97})
                    log(f"  {t['id']:18s} {wall:7.1f}s {rec['tok_s']:5.1f}tk/s tok={ev}/{np} trunc={rec['truncated']} score={chk['score']}")
                except Exception as e:
                    rec.update({'ok': False, 'error': str(e)[:160]})
                    log(f"  {t['id']:18s} ERRORE {str(e)[:80]}")
                out.write(json.dumps(rec, ensure_ascii=False)+"\n"); out.flush()
            try: urllib.request.urlopen(urllib.request.Request(OLLAMA, data=json.dumps({'model': m['name'], 'prompt': 'ok', 'keep_alive': '0', 'stream': False}).encode(), headers={'Content-Type': 'application/json'}), timeout=60)
            except Exception: pass
    log("FINITO open puliti.")

if __name__ == '__main__':
    main()
