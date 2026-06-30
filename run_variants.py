#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RUN 2 — varianti: THINKING on/off (per i modelli che lo supportano) + CAVEMAN (per i modelli grossi).
Per l'articolo: "il no-thinking spesso vince sui task strutturati" + "lo stile telegrafico aiuta o no?".
Deadline-aware, salva incrementale in results/results_variants_<ts>.jsonl (campo 'mode').
Uso: python3 run_variants.py --until 10:45
"""
import json, time, sys, os, argparse, datetime, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from tasks import TASKS
OLLAMA = "http://localhost:11434/api/generate"

CAVE = ("[STILE CAVEMAN: risposta TELEGRAFICA — parole minime, niente cortesie né spiegazioni superflue, "
        "solo l'essenziale. Ma se devi scrivere CODICE o JSON: completo, corretto, valido (NON accorciare il codice).]")

# Modelli che supportano il "thinking" + come si attiva
THINK_MODELS = [
    {'name': 'cogito:8b',    'lab': 'Cogito 8B',    'how': 'system'},   # system "Enable deep thinking subroutine."
    {'name': 'gemma4:12b',   'lab': 'Gemma4 12B',   'how': 'flag'},     # think:true + num_predict alto
    {'name': 'gemma4:31b',   'lab': 'Gemma4 31B',   'how': 'flag', 'heavy': True},
    {'name': 'qwen3.6:35b',  'lab': 'Qwen3.6 35B',  'how': 'flag', 'heavy': True},
]
# Modelli su cui provare il caveman (incluso gemma4:12b, il cavallo di battaglia)
CAVEMAN_MODELS = [
    {'name': 'gemma4:12b',                                                         'lab': 'Gemma4 12B'},
    {'name': 'gemma4:31b',                                                         'lab': 'Gemma4 31B'},
    {'name': 'qwen3.6:35b',                                                        'lab': 'Qwen3.6 35B (MoE)'},
    {'name': 'hf.co/bartowski/Qwen2.5-Coder-32B-Instruct-abliterated-GGUF:Q4_K_M', 'lab': 'Qwen2.5-Coder 32B abliterated'},
    {'name': 'hf.co/mradermacher/Llama-3.3-70B-Instruct-abliterated-GGUF:Q3_K_M',  'lab': 'Llama-3.3 70B abliterated'},
]
# sottoinsieme di task significativi (no siti: troppo lenti per i grossi + thinking)
SUB_IDS = ['intent_sconto', 'menu_struttura', 'allergeni', 'config_pizzeria',
           'strategia_martedi', 'strategia_feature', 'ricetta_vegana', 'code_endpoint', 'code_review', 'copy_prodotto']
SUB = [t for t in TASKS if t['id'] in SUB_IDS]

def log(*a): print(f"[{datetime.datetime.now():%H:%M:%S}]", *a, flush=True)

def installed(name):
    try:
        r = urllib.request.urlopen("http://localhost:11434/api/tags", timeout=10)
        return name in {m['name'] for m in json.loads(r.read()).get('models', [])}
    except Exception:
        return False

def call(model, prompt, system, num_predict, want_json, think=False, timeout=900):
    body = {'model': model, 'prompt': prompt, 'system': system, 'stream': False,
            'think': bool(think), 'keep_alive': '25m',
            'options': {'temperature': 0.2 if want_json else 0.5, 'num_predict': num_predict}}
    if want_json:
        body['format'] = 'json'
    t0 = time.time()
    r = urllib.request.urlopen(urllib.request.Request(
        OLLAMA, data=json.dumps(body).encode(), headers={'Content-Type': 'application/json'}), timeout=timeout)
    j = json.loads(r.read()); wall = time.time() - t0
    ev = j.get('eval_count') or 0; evd = (j.get('eval_duration') or 0) / 1e9
    return {'response': j.get('response', ''), 'wall_s': round(wall, 2), 'tokens': ev,
            'tok_s': round(ev / evd, 2) if evd > 0 else 0}

def unload(model):
    try: call(model, 'ok', '', 1, False, timeout=60)
    except Exception: pass

def run_task(out, model, lab, task, mode, think, sysprefix=''):
    want_json = (task['expects'] == 'json')
    sysmsg = (sysprefix + task.get('sys', '')).strip()
    np = task['np']
    # token floor anti-troncamento sui task aperti (verbosi): non penalizzare per il tetto token
    if task['cat'] in ('strategy', 'recipe', 'code'):
        np = max(np, 1100)
    elif task['cat'] == 'website':
        np = max(np, 4000)
    elif task['cat'] == 'copy':
        np = max(np, 400)
    if think:
        np = max(np, 2600)   # il ragionamento mangia token: serve num_predict alto (bug-trap gemma)
    rec = {'model': model, 'model_lab': lab, 'mode': mode, 'think': bool(think),
           'task': task['id'], 'cat': task['cat'], 'expects': task['expects'],
           'ts': datetime.datetime.now().isoformat(timespec='seconds')}
    try:
        res = call(model, task['prompt'], sysmsg, np, want_json, think=think)
        chk = task['check'](res['response'])
        rec.update({k: res[k] for k in ('wall_s', 'tokens', 'tok_s')})
        rec['check'] = chk; rec['response'] = res['response']; rec['ok'] = True
        log(f"  [{mode:9s}] {lab:22s} {task['id']:18s} {res['wall_s']:6.1f}s {res['tok_s']:5.1f}tk/s check={chk['passed']}({chk['score']})")
    except Exception as e:
        rec.update({'ok': False, 'error': str(e)[:160]})
        log(f"  [{mode:9s}] {lab:22s} {task['id']:18s} ERRORE {str(e)[:80]}")
    out.write(json.dumps(rec, ensure_ascii=False) + "\n"); out.flush()

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--until', default='10:45')
    args = ap.parse_args()
    hh, mm = map(int, args.until.split(':')); now = datetime.datetime.now()
    deadline = now.replace(hour=hh, minute=mm, second=0, microsecond=0)
    if deadline <= now: deadline += datetime.timedelta(days=1)
    log(f"deadline {deadline:%H:%M} · {len(SUB)} task")
    ts = f"{now:%Y%m%d_%H%M}"; outp = os.path.join(HERE, 'results', f'results_variants_{ts}.jsonl')
    json.dump({'started': str(now), 'deadline': str(deadline), 'kind': 'variants'},
              open(os.path.join(HERE, 'results', f'run_variants_{ts}.json'), 'w'))
    log(f"output {outp}")

    with open(outp, 'a') as out:
        # ── A) THINKING off vs on ──
        for m in THINK_MODELS:
            if datetime.datetime.now() >= deadline: log("deadline"); break
            if not installed(m['name']): log(f"skip {m['lab']}"); continue
            log(f"=== THINKING: {m['lab']} ===")
            tasks = SUB[:5] if m.get('heavy') else SUB   # sui pesanti meno task (thinking è lentissimo)
            for think in (False, True):
                pref = "Enable deep thinking subroutine.\n" if (think and m['how'] == 'system') else ''
                flag = think and m['how'] == 'flag'
                for t in tasks:
                    if datetime.datetime.now() >= deadline: break
                    run_task(out, m['name'], m['lab'], t, 'think_on' if think else 'think_off', flag, pref)
            unload(m['name'])
        # ── B) CAVEMAN sui grossi ──
        for m in CAVEMAN_MODELS:
            if datetime.datetime.now() >= deadline: log("deadline"); break
            if not installed(m['name']): log(f"skip {m['lab']}"); continue
            log(f"=== CAVEMAN: {m['lab']} ===")
            for t in SUB:
                if datetime.datetime.now() >= deadline: break
                run_task(out, m['name'], m['lab'], t, 'caveman', False, CAVE + "\n\n")
            unload(m['name'])
    log("FINITO varianti.")

if __name__ == '__main__':
    main()
