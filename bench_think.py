#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Re-run dei modelli REASONING con think: true.
Poi giudica tutto con il modello migliore (gemma4:26b).
"""
import json, time, sys, os, urllib.request, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
OLLAMA = "http://localhost:11434/api/generate"

# modelli con thinking/reasoning
THINK_MODELS = [
    'deepseek-r1:14b',
    'deepseek-r1:8b',
    'qwen3.6:35b',
    'qwen3.5:latest',
    'qwen3:4b',
    'cogito:8b',
]

# carica task
sys.path.insert(0, HERE)
from tasks_realworld import REAL_TASKS

def log(*a, end='\n', flush=True):
    print(f"[{datetime.datetime.now():%H:%M:%S}]", *a, end=end, flush=flush)

def call_think(model, prompt, system, num_predict, timeout=300):
    body = {
        'model': model, 'prompt': prompt, 'system': system, 'stream': False,
        'think': True, 'keep_alive': '5m',
        'options': {'temperature': 0.5, 'num_predict': num_predict}
    }
    data = json.dumps(body).encode()
    t0 = time.time()
    r = urllib.request.urlopen(urllib.request.Request(
        OLLAMA, data=data, headers={'Content-Type': 'application/json'}), timeout=timeout)
    j = json.loads(r.read())
    wall = time.time() - t0
    resp = j.get('response', '')
    thinking = j.get('thinking', '')
    ev = j.get('eval_count') or 0
    evd = (j.get('eval_duration') or 0) / 1e9
    return {
        'response': resp, 'thinking': thinking,
        'wall_s': round(wall, 2), 'tokens': ev,
        'tok_s': round(ev/evd, 2) if evd > 0 else 0,
    }

def unload(model):
    try:
        body = {'model': model, 'prompt': 'ok', 'stream': False, 'keep_alive': '0',
                'options': {'num_predict': 1}}
        urllib.request.urlopen(urllib.request.Request(
            OLLAMA, data=json.dumps(body).encode(), headers={'Content-Type': 'application/json'}), timeout=30)
    except: pass

def judge_one(model, task_prompt, response):
    """gemma4:26b giudica la risposta"""
    prompt = (
        "Sei un valutatore severo e imparziale.\n\n"
        f"COMPITO: {task_prompt[:1500]}\n\n"
        f"RISPOSTA:\n<<<\n{response[:4000]}\n>>>\n\n"
        "Voto 1-5 + motivazione. JSON: {\"voto\":N,\"perche\":\"...\"}"
    )
    body = {
        'model': 'gemma4:26b', 'prompt': prompt, 'stream': False, 'think': False,
        'format': 'json', 'keep_alive': '30m',
        'options': {'temperature': 0.0, 'num_predict': 200}
    }
    data = json.dumps(body).encode()
    r = urllib.request.urlopen(urllib.request.Request(
        OLLAMA, data=data, headers={'Content-Type': 'application/json'}), timeout=300)
    out = json.loads(r.read()).get('response', '')
    try:
        d = json.loads(out)
        v = int(d.get('voto', 0))
        return max(1, min(5, v)), str(d.get('perche', ''))[:100]
    except:
        return 0, 'parse-fail'

def main():
    ts = datetime.datetime.now().strftime('%Y%m%d_%H%M')
    out_path = os.path.join(HERE, 'results', f'results_think_{ts}.jsonl')
    judged_path = os.path.join(HERE, 'results', f'judged_think_{ts}.jsonl')

    log(f"=== RE-RUN CON THINK: ON ===")
    log(f"Modelli: {len(THINK_MODELS)} | Task: {len(REAL_TASKS)}")
    log(f"Output: {out_path}")

    # FASE 1: ri-test con thinking ON
    all_results = []
    with open(out_path, 'w') as out:
        for model in THINK_MODELS:
            log(f"\n🤖 {model} (think: ON)")
            for t in REAL_TASKS:
                np = min(t['np'], 800)
                log(f"  {t['id']}...", end=' ', flush=True)
                try:
                    res = call_think(model, t['prompt'], t.get('sys',''), np)
                    rec = {
                        'model': model, 'task': t['id'], 'cat': t['cat'],
                        'think': True, 'ok': True,
                        'response': res['response'], 'thinking': res['thinking'],
                        'wall_s': res['wall_s'], 'tok_s': res['tok_s'],
                        'ts': datetime.datetime.now().isoformat(timespec='seconds')
                    }
                    log(f"✅ {res['wall_s']:.0f}s {res['tok_s']:.0f}tk/s think={len(res['thinking'])}char")
                except Exception as e:
                    rec = {
                        'model': model, 'task': t['id'], 'cat': t['cat'],
                        'think': True, 'ok': False, 'error': str(e)[:100],
                        'response': '', 'thinking': '',
                        'ts': datetime.datetime.now().isoformat(timespec='seconds')
                    }
                    log(f"❌ {str(e)[:60]}")
                out.write(json.dumps(rec, ensure_ascii=False) + "\n")
                out.flush()
                all_results.append(rec)
            unload(model)

    # FASE 2: giudica con gemma4:26b
    log(f"\n\n🧑‍⚖️ FASE 2: gemma4:26b giudica {len(all_results)} risposte (think: ON)")
    prompts = {t['id']: t['prompt'] for t in REAL_TASKS}

    with open(judged_path, 'w') as out:
        for i, rec in enumerate(all_results, 1):
            m = rec['model']
            tid = rec['task']
            resp = rec.get('response', '')
            prompt = prompts.get(tid, '')

            if not rec.get('ok'):
                voto, why = 0, 'errore'
                final = 0.0
            else:
                voto, why = judge_one(m, prompt, resp)
                final = round((voto-1)/4, 3) if voto else 0.0

            rec['judge_voto'] = voto
            rec['judge_why'] = why
            rec['judge_score'] = final
            out.write(json.dumps(rec, ensure_ascii=False) + "\n")
            out.flush()

            star = '⭐'*voto if voto else '❌'
            log(f"  [{i:>3}/{len(all_results)}] {m:25s} {tid:22s} {star} {voto}/5")

    # FASE 3: classifica
    from collections import defaultdict
    agg = defaultdict(lambda: {'pts':[], 'walls':[]})
    for rec in all_results:
        m = rec['model']
        agg[m]['pts'].append(rec.get('judge_score', 0))
        agg[m]['walls'].append(rec.get('wall_s', 0))

    log(f"\n{'='*65}")
    log(f"🏆 CLASSIFICA THINK: ON (giudice: gemma4:26b)")
    log(f"{'='*65}")
    rank = sorted(
        [(m, sum(v['pts'])/len(v['pts']), sum(v['walls'])/len(v['walls']))
         for m,v in agg.items()],
        key=lambda x: (-x[1], x[2])
    )
    for i,(m,sc,t) in enumerate(rank,1):
        voto = round(sc*4+1,1)
        log(f"  {i}. {m:<25s} {sc:.3f} ({voto}/5) {t:.0f}s")

    # salva classifica
    json.dump(rank, open(os.path.join(HERE, 'results', f'rank_think_{ts}.json'), 'w'),
              indent=2)
    log(f"\nSalvato: {judged_path}")

if __name__ == '__main__':
    main()
