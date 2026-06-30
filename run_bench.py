#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Benchmark "Non esiste il modello migliore" — esegue ogni TASK su ogni MODELLO locale (Ollama),
misura tempo/token/tok-s, applica controlli automatici, salva incrementale (JSONL) ed è
DEADLINE-AWARE (si ferma all'ora limite senza perdere i dati già raccolti).

Uso:
  python3 run_bench.py                 # tutti i modelli/task, deadline default 06:45
  python3 run_bench.py --until 06:30   # ferma a quell'ora
  python3 run_bench.py --models cogito:8b,gemma4:12b --quick   # subset di prova
"""
import json, time, sys, os, argparse, datetime, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from tasks import TASKS  # noqa

OLLAMA = "http://localhost:11434/api/generate"

# Modelli da confrontare. tier 'heavy' = gira su CPU/RAM (lento) → num_predict ridotto e task pesanti capati.
MODELS = [
    {'name': 'qwen2.5:3b',                                                         'tier': 'light', 'lab': 'Qwen2.5 3B (default)'},
    {'name': 'cogito:8b',                                                          'tier': 'light', 'lab': 'Cogito 8B'},
    {'name': 'gemma4:12b',                                                         'tier': 'light', 'lab': 'Gemma4 12B'},
    {'name': 'qwen2.5-coder:14b',                                                  'tier': 'light', 'lab': 'Qwen2.5-Coder 14B'},
    {'name': 'deepseek-coder-v2:16b',                                              'tier': 'light', 'lab': 'DeepSeek-Coder-V2 16B'},
    {'name': 'gemma4:31b',                                                         'tier': 'heavy', 'lab': 'Gemma4 31B'},
    {'name': 'qwen3.6:35b',                                                        'tier': 'heavy', 'lab': 'Qwen3.6 35B (MoE)'},
    {'name': 'hf.co/bartowski/Qwen2.5-Coder-32B-Instruct-abliterated-GGUF:Q4_K_M', 'tier': 'heavy', 'lab': 'Qwen2.5-Coder 32B abliterated'},
    {'name': 'hf.co/mradermacher/Llama-3.3-70B-Instruct-abliterated-GGUF:Q3_K_M',  'tier': 'heavy', 'lab': 'Llama-3.3 70B abliterated'},
]

def log(*a):
    print(f"[{datetime.datetime.now():%H:%M:%S}]", *a, flush=True)

def ollama_installed(name):
    try:
        r = urllib.request.urlopen("http://localhost:11434/api/tags", timeout=10)
        tags = {m['name'] for m in json.loads(r.read()).get('models', [])}
        return name in tags
    except Exception:
        return False

def call(model, prompt, system, num_predict, want_json, keep_alive='25m', timeout=900):
    body = {'model': model, 'prompt': prompt, 'system': system, 'stream': False,
            'think': False, 'keep_alive': keep_alive,
            'options': {'temperature': 0.2 if want_json else 0.5, 'num_predict': num_predict}}
    if want_json:
        body['format'] = 'json'
    data = json.dumps(body).encode()
    t0 = time.time()
    r = urllib.request.urlopen(urllib.request.Request(
        OLLAMA, data=data, headers={'Content-Type': 'application/json'}), timeout=timeout)
    j = json.loads(r.read())
    wall = time.time() - t0
    ev = j.get('eval_count') or 0
    evd = (j.get('eval_duration') or 0) / 1e9
    return {
        'response': j.get('response', ''),
        'wall_s': round(wall, 2),
        'tokens': ev,
        'tok_s': round(ev / evd, 2) if evd > 0 else 0,
        'load_s': round((j.get('load_duration') or 0) / 1e9, 2),
        'prompt_tokens': j.get('prompt_eval_count') or 0,
    }

def unload(model):
    try:
        call(model, 'ok', '', 1, False, keep_alive='0', timeout=60)
    except Exception:
        pass

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--until', default='06:45', help='ora limite HH:MM')
    ap.add_argument('--models', default='', help='subset CSV')
    ap.add_argument('--quick', action='store_true', help='solo 3 task per prova')
    args = ap.parse_args()

    hh, mm = map(int, args.until.split(':'))
    now = datetime.datetime.now()
    deadline = now.replace(hour=hh, minute=mm, second=0, microsecond=0)
    if deadline <= now:
        deadline += datetime.timedelta(days=1)
    log(f"deadline: {deadline:%Y-%m-%d %H:%M}")

    models = MODELS
    if args.models:
        want = set(args.models.split(','))
        models = [m for m in MODELS if m['name'] in want or m['lab'] in want]
    tasks = TASKS[:3] if args.quick else TASKS

    ts = f"{now:%Y%m%d_%H%M}"
    out_path = os.path.join(HERE, 'results', f'results_{ts}.jsonl')
    meta_path = os.path.join(HERE, 'results', f'run_{ts}.json')
    json.dump({'started': str(now), 'deadline': str(deadline),
               'models': [m['name'] for m in models], 'n_tasks': len(tasks)},
              open(meta_path, 'w'), indent=2)
    log(f"output: {out_path}")

    n_done = 0
    with open(out_path, 'a') as out:
        for m in models:
            if datetime.datetime.now() >= deadline:
                log("DEADLINE raggiunta, stop."); break
            if not ollama_installed(m['name']):
                log(f"SKIP {m['lab']} (non installato)"); continue
            log(f"=== MODELLO: {m['lab']} ({m['tier']}) ===")
            for t in tasks:
                if datetime.datetime.now() >= deadline:
                    log("DEADLINE durante il modello, stop."); break
                # i task pesanti (siti) su modelli heavy = num_predict ridotto per non sforare
                np = t['np']
                if m['tier'] == 'heavy' and t['cat'] == 'website':
                    np = min(np, 1400)
                want_json = (t['expects'] == 'json')
                rec = {'model': m['name'], 'model_lab': m['lab'], 'tier': m['tier'],
                       'task': t['id'], 'cat': t['cat'], 'expects': t['expects'],
                       'ts': datetime.datetime.now().isoformat(timespec='seconds')}
                try:
                    res = call(m['name'], t['prompt'], t.get('sys', ''), np, want_json)
                    chk = t['check'](res['response'])
                    rec.update({k: res[k] for k in ('wall_s', 'tokens', 'tok_s', 'load_s', 'prompt_tokens')})
                    rec['check'] = chk
                    rec['response'] = res['response']
                    rec['ok'] = True
                    log(f"  {t['id']:18s} {res['wall_s']:6.1f}s {res['tok_s']:5.1f}tk/s  "
                        f"check={chk['passed']} ({chk['score']}) {chk['note']}")
                except Exception as e:
                    rec.update({'ok': False, 'error': str(e)[:200]})
                    log(f"  {t['id']:18s} ERRORE: {str(e)[:120]}")
                out.write(json.dumps(rec, ensure_ascii=False) + "\n"); out.flush()
                n_done += 1
            unload(m['name'])
            log(f"  (scaricato {m['lab']} dalla VRAM)")
    log(f"FINITO. {n_done} test salvati in {out_path}")

if __name__ == '__main__':
    main()
