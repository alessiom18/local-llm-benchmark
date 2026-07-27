#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Benchmark REAL-WORLD — testa tutti i modelli Ollama su task complessi e reali.
Misure: tempo, token/s, qualità (check automatico), completezza.

Task types:
  - investigate: analizza codice, trova problemi
  - diagnose: trova il bug, spiega la causa
  - create: genera documentazione, codice, dispense
  - search: cerca informazioni, sintetizza
  - fix: correggi codice errato
  - predict: anticipa problemi futuri
  - multi_step: compiti con più fasi

SAFE: niente modifiche al sistema, solo lettura e generazione.
"""
import json, time, sys, os, argparse, datetime, urllib.request, re

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

OLLAMA = "http://localhost:11434/api/generate"

# ---- TUTTI I MODELLI DISPONIBILI ----
def get_all_models():
    """Scansiona Ollama e restituisce tutti i modelli (esclusi embedding/vision puri)."""
    try:
        r = urllib.request.urlopen("http://localhost:11434/api/tags", timeout=10)
        tags = json.loads(r.read()).get('models', [])
        skip = {'nomic-embed-text', 'moondream', 'llava', 'llava:7b'}
        models = []
        for m in tags:
            name = m['name']
            base = name.split(':')[0].split('/')[-1]
            if base in skip or name in skip:
                continue
            # classifica per dimensione
            size_gb = m.get('size', 0) / 1e9
            tier = 'light' if size_gb < 12 else 'heavy'
            models.append({'name': name, 'tier': tier, 'size_gb': round(size_gb, 1)})
        return models
    except Exception as e:
        print(f"ERRORE connessione Ollama: {e}")
        return []

# ---- CHECK FUNCTIONS ----
def _try_json(txt):
    txt = txt.strip()
    m = re.search(r'```(?:json)?\s*(.*?)```', txt, re.S)
    if m: txt = m.group(1).strip()
    s = re.search(r'[\{\[]', txt)
    if s: txt = txt[s.start():]
    try: return json.loads(txt)
    except: pass
    for end in (txt.rfind('}'), txt.rfind(']')):
        if end > 0:
            try: return json.loads(txt[:end+1])
            except: pass
    return None

def chk_json_keys(keys):
    def f(txt):
        d = _try_json(txt)
        if d is None: return {'passed': False, 'score': 0.0, 'note': 'JSON non valido'}
        obj = d[0] if isinstance(d, list) and d else d
        if not isinstance(obj, dict): return {'passed': False, 'score': 0.3, 'note': 'non è un dict'}
        have = [k for k in keys if k in obj]
        sc = len(have) / len(keys)
        return {'passed': sc >= 0.6, 'score': round(sc, 2), 'note': f'{len(have)}/{len(keys)} chiavi'}
    return f

def chk_nonempty(txt):
    n = len(txt.strip())
    return {'passed': n > 50, 'score': 1.0 if n > 50 else n/50, 'note': f'{n} char'}

def chk_code(txt):
    has_def = bool(re.search(r'def\s+\w+\s*\(', txt))
    has_return = 'return' in txt
    has_import = 'import' in txt or 'from ' in txt
    sc = (has_def + has_return + has_import) / 3
    return {'passed': has_def and has_return, 'score': round(sc, 2),
            'note': f'def={has_def} return={has_return} import={has_import}'}

def chk_code_bugfix(original_code, fixed_code):
    """Verifica che il codice fixato sia diverso dall'originale e contenga fix."""
    def f(txt):
        changed = txt.strip() != original_code.strip()
        has_explanation = len(txt) > 100
        has_fix = 'fix' in txt.lower() or 'corregg' in txt.lower() or 'bug' in txt.lower() or 'risolv' in txt.lower()
        sc = (changed + has_explanation + has_fix) / 3
        return {'passed': changed and has_explanation, 'score': round(sc, 2),
                'note': f'changed={changed} explained={has_explanation} identified={has_fix}'}
    return f

def chk_text_len(lo, hi):
    def f(txt):
        n = len(txt.split())
        if n < lo: sc = n / lo
        elif n > hi: sc = max(0.3, hi / n)
        else: sc = 1.0
        return {'passed': lo <= n <= hi, 'score': round(sc, 2), 'note': f'{n} parole (atteso {lo}-{hi})'}
    return f

def chk_diagnosis(txt):
    """Verifica che una diagnosi contenga: problema, causa, soluzione."""
    t = txt.lower()
    has_problem = any(w in t for w in ['problema', 'errore', 'guasto', 'bug', 'difetto'])
    has_cause = any(w in t for w in ['causa', 'perché', 'ragione', 'motivo', 'origine'])
    has_solution = any(w in t for w in ['soluzione', 'fix', 'corregg', 'risolv', 'sostitu', 'ripair'])
    has_test = any(w in t for w in ['test', 'verif', 'controll', 'misur'])
    sc = (has_problem + has_cause + has_solution + has_test) / 4
    return {'passed': has_problem and has_solution, 'score': round(sc, 2),
            'note': f'prob={has_problem} cause={has_cause} sol={has_solution} test={has_test}'}

def chk_multistep(txt):
    """Verifica che la risposta contenga passi multipli."""
    t = txt.lower()
    steps = len(re.findall(r'(?:\d+[\.\)]\s|step\s|fase\s|prima\s|poi\s|dopodiché\s|infine\s)', t))
    has_structure = steps >= 2
    has_detail = len(txt) > 300
    sc = min(1.0, steps / 4) * (1.0 if has_detail else 0.5)
    return {'passed': has_structure and has_detail, 'score': round(sc, 2),
            'note': f'{steps} passi, {len(txt)} char'}

def chk_prediction(txt):
    """Verifica che una predizione contenga: scenario, rischio, mitigazione."""
    t = txt.lower()
    has_scenario = any(w in t for w in ['scenario', 'caso', 'situazione', 'quando', 'se'])
    has_risk = any(w in t for w in ['rischio', 'problema', 'guasto', 'fallimento', 'pericolo'])
    has_mitigation = any(w in t for w in ['mitigaz', 'preven', 'evitare', 'protegg', 'backup'])
    sc = (has_scenario + has_risk + has_mitigation) / 3
    return {'passed': has_scenario and has_risk, 'score': round(sc, 2),
            'note': f'scenario={has_scenario} rischio={has_risk} mitig={has_mitigation}'}

def chk_search(txt):
    """Verifica che una ricerca sia completa e strutturata."""
    t = txt.lower()
    has_sources = any(w in t for w in ['fonte', 'documentaz', 'manuale', 'specifiche', ' datasheet'])
    has_comparison = any(w in t for w in ['confronto', 'differenza', 'vantaggio', 'svantaggio', 'alternativ'])
    has_recommendation = any(w in t for w in ['consiglio', 'raccomand', 'sugger', 'meglio', 'ideale'])
    has_detail = len(txt) > 200
    sc = (has_sources + has_comparison + has_recommendation + has_detail) / 4
    return {'passed': has_detail and (has_sources or has_comparison), 'score': round(sc, 2),
            'note': f'source={has_sources} confronto={has_comparison} consiglio={has_recommendation}'}


# ---- TASKS REAL-WORLD ----
CODE_WITH_BUG = '''@app.route("/api/bilancia", methods=["POST"])
def bilancia():
    data = request.json
    cella = data["cella"]
    target = data["target_voltage"]
    db.execute("UPDATE celle SET voltage = ? WHERE id = ?", (target, cella))
    return jsonify({"ok": True})'''

REAL_TASKS = [
    # === INVESTIGATE ===
    {'id': 'inv_find_bug', 'cat': 'investigate', 'expects': 'text', 'np': 600,
     'sys': 'Sei un senior developer. Analizzi codice e trovi problemi di sicurezza e logica.',
     'prompt': f'Analizza questo codice Flask e trova TUTTI i problemi (sicurezza, logica, errori). '
               f'Spiegali in ordine di gravità:\n```python\n{CODE_WITH_BUG}\n```',
     'check': chk_diagnosis},

    # === DIAGNOSE ===
    {'id': 'diag_ev_system', 'cat': 'diagnose', 'expects': 'text', 'np': 600,
     'sys': 'Sei un tecnico EV esperto. Diagnostiche sistematiche e precise.',
     'prompt': 'Un veicolo elettrico 48V ha questi sintomi: parte, va per 5 minuti, poi si ferma. '
               'Display mostra "E-03". Dopo 10 minuti riparte. Riparte dopo 5 minuti. '
               'Fai una diagnosi completa: possibili cause, test da fare, soluzione.',
     'check': chk_diagnosis},

    # === CREATE (dispensa tecnica) ===
    {'id': 'create_dispensa', 'cat': 'create', 'expects': 'text', 'np': 1200,
     'sys': 'Sei un formatore EV. Scrivi dispense pratiche, italiane, da officina.',
     'prompt': 'Scrivi una dispensa pratica (massimo 2 pagine) su "Come diagnosticare un BMS guasto". '
               'Deve avere: cosa serve, come si misura, errori comuni, quando chiedere aiuto. '
               'Italiano semplice, elenchi puntati, emoji per i punti chiave.',
     'check': chk_text_len(150, 800)},

    # === SEARCH (ricerca tecnica) ===
    {'id': 'search_mosfet', 'cat': 'search', 'expects': 'text', 'np': 600,
     'sys': 'Sei un esperto di componenti elettronici. Fai ricerche accurate e practically oriented.',
     'prompt': 'Confronta MOSFET per controller EV: IRF3205 vs IRF1404 vs IRFZ44N. '
               'Per ogni uno: specifiche, prezzo indicativo, dove si trova, pro/contro. '
               'Quale scegliere per un motorino 48V 1000W e perché.',
     'check': chk_search},

    # === FIX (correggi codice) ===
    {'id': 'fix_injection', 'cat': 'fix', 'expects': 'text', 'np': 600,
     'sys': 'Sei un sicurezzista. Correggi vulnerabilità senza rompere la funzionalità.',
     'prompt': f'Correggi questo codice eliminando la SQL injection. Spiega ogni modifica:\n```python\n{CODE_WITH_BUG}\n```',
     'check': chk_code_bugfix(CODE_WITH_BUG, '')},

    # === PREDICT (prevedi problemi) ===
    {'id': 'predict_batt_degrad', 'cat': 'predict', 'expects': 'text', 'np': 600,
     'sys': 'Sei un esperto di batterie EV. Prevedi problemi e proponi mitigazioni.',
     'prompt': 'Un utente ha una bici elettrica 48V 20Ah con 300 cicli. '
               'Vive a Livorno (clima mite). Va al lavoro 10km al giorno. '
               'Prevedi i problemi che avrà nei prossimi 6 mesi e come prevenirli.',
     'check': chk_prediction},

    # === MULTI-STEP (compito complesso) ===
    {'id': 'multi_build_scooter', 'cat': 'multi_step', 'expects': 'text', 'np': 1200,
     'sys': 'Sei un EV builder esperto. Fai un piano completo e dettagliato.',
     'prompt': 'Voglio convertire un Piaggio Ciao 50 in elettrico. Budget 800€. '
               'Voglio almeno 40km di autonomia e 45km/h. '
               'Fai un piano completo: componenti (con prezzi), fasi di lavoro, '
               'tempistiche, rischi, cosa posso fare da solo e cosa delegare.',
     'check': chk_multistep},

    # === CODE (genera codice reale) ===
    {'id': 'code_battery_monitor', 'cat': 'create', 'expects': 'code', 'np': 800,
     'sys': 'Sei uno sviluppatore Python embedded. Codice pratico e testato.',
     'prompt': 'Scrivi uno script Python che: '
               '1) Legge la tensione di una cella Li-ion via ADC ADS1115 '
               '2) Calcola lo stato di carica (SOC) con curva approssimativa '
               '3) Accende un LED verde se >50%, giallo se 20-50%, rosso se <20% '
               '4) Logga tutto su file CSV con timestamp. '
               'Include gestione errori e commenti minimi.',
     'check': chk_code},

    # === RICERCA + SINTESI ===
    {'id': 'search_tools', 'cat': 'search', 'expects': 'text', 'np': 600,
     'sys': 'Sei un esperto di strumenti da officina EV.',
     'prompt': 'Quali sono i 5 strumenti INDISPENSABILI per un officina EV? '
               'Per ognuno: marca/modello consigliato, prezzo, dove comprarlo in Italia, '
               'perché è fondamentale. Ordine per importanza.',
     'check': chk_search},

    # === DEBUG REALISTICO ===
    {'id': 'diag_comm_error', 'cat': 'diagnose', 'expects': 'text', 'np': 600,
     'sys': 'Sei un tecnico diagnostico EV.',
     'prompt': 'Un display EV mostra dati di velocità erratici (va da 0 a 999 km/h random). '
               'La velocità reale è costante a 25km/h. Il sensore Hall è nuovo. '
               'I cavi sono stati sostituiti di recente. '
               'Diagnostica il problema passo per passo.',
     'check': chk_diagnosis},
]

# ---- OLLAMA CALL ----
def call(model, prompt, system, num_predict, want_json, timeout=300):
    body = {'model': model, 'prompt': prompt, 'system': system, 'stream': False,
            'think': False, 'keep_alive': '5m',
            'options': {'temperature': 0.2 if want_json else 0.5, 'num_predict': num_predict}}
    if want_json: body['format'] = 'json'
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
    try: call(model, 'ok', '', 1, False, keep_alive='0', timeout=30)
    except: pass

def log(*a, end='\n', flush=True):
    print(f"[{datetime.datetime.now():%H:%M:%S}]", *a, end=end, flush=flush)


# ---- MAIN ----
def main():
    ap = argparse.ArgumentParser(description="Benchmark REAL-WORLD su tutti i modelli")
    ap.add_argument('--models', default='', help='subset CSV (default: tutti)')
    ap.add_argument('--tasks', default='', help='subset task IDs CSV')
    ap.add_argument('--quick', action='store_true', help='solo 3 task per prova')
    ap.add_argument('--until', default='23:59', help='deadline HH:MM')
    ap.add_argument('--timeout', type=int, default=300, help='timeout per task (sec)')
    args = ap.parse_args()

    hh, mm = map(int, args.until.split(':'))
    now = datetime.datetime.now()
    deadline = now.replace(hour=hh, minute=mm, second=0, microsecond=0)
    if deadline <= now: deadline += datetime.timedelta(days=1)

    models = get_all_models()
    if args.models:
        want = set(args.models.split(','))
        models = [m for m in models if m['name'] in want]

    tasks = REAL_TASKS
    if args.tasks:
        want_t = set(args.tasks.split(','))
        tasks = [t for t in tasks if t['id'] in want_t]
    elif args.quick:
        tasks = tasks[:3]

    ts = now.strftime('%Y%m%d_%H%M')
    out_path = os.path.join(HERE, 'results', f'results_realworld_{ts}.jsonl')
    meta_path = os.path.join(HERE, 'results', f'run_realworld_{ts}.json')
    os.makedirs(os.path.join(HERE, 'results'), exist_ok=True)

    json.dump({'started': str(now), 'deadline': str(deadline),
               'models': [m['name'] for m in models], 'n_tasks': len(tasks),
               'task_ids': [t['id'] for t in tasks]},
              open(meta_path, 'w'), indent=2)

    log(f"=== BENCHMARK REAL-WORLD ===")
    log(f"Modelli: {len(models)} | Task: {len(tasks)} | Deadline: {deadline:%H:%M}")
    log(f"Output: {out_path}")

    n_done = 0
    results_summary = []

    with open(out_path, 'a') as out:
        for m in models:
            if datetime.datetime.now() >= deadline:
                log("DEADLINE raggiunta, stop."); break

            log(f"\n{'='*60}")
            log(f"🤖 MODELLO: {m['name']} ({m['tier']}, {m['size_gb']}GB)")
            log(f"{'='*60}")

            model_results = {'model': m['name'], 'tier': m['tier'], 'tasks': []}
            t_start = time.time()

            for t in tasks:
                if datetime.datetime.now() >= deadline:
                    log("DEADLINE durante il modello, stop."); break

                want_json = (t['expects'] == 'json')
                np = t['np']
                # riduci token per modelli heavy
                if m['tier'] == 'heavy': np = min(np, 800)

                log(f"\n  📋 {t['id']} ({t['cat']})...", end=' ', flush=True)

                rec = {'model': m['name'], 'task': t['id'], 'cat': t['cat'],
                       'ts': datetime.datetime.now().isoformat(timespec='seconds')}

                try:
                    res = call(m['name'], t['prompt'], t.get('sys', ''), np, want_json,
                               timeout=args.timeout)
                    chk = t['check'](res['response'])
                    rec.update({k: res[k] for k in ('wall_s', 'tokens', 'tok_s', 'load_s', 'prompt_tokens')})
                    rec['check'] = chk
                    rec['response'] = res['response']
                    rec['ok'] = True
                    log(f"✅ {res['wall_s']:.1f}s {res['tok_s']:.1f}tk/s check={chk['score']:.2f}")
                except Exception as e:
                    rec.update({'ok': False, 'error': str(e)[:200]})
                    log(f"❌ {str(e)[:80]}")

                out.write(json.dumps(rec, ensure_ascii=False) + "\n")
                out.flush()
                model_results['tasks'].append(rec)
                n_done += 1

            total_s = time.time() - t_start
            avg_score = sum(r.get('check', {}).get('score', 0) for r in model_results['tasks']) / max(1, len(model_results['tasks']))
            ok_count = sum(1 for r in model_results['tasks'] if r.get('ok', False))

            model_results['total_s'] = round(total_s, 1)
            model_results['avg_score'] = round(avg_score, 3)
            model_results['ok_count'] = ok_count
            model_results['total_tasks'] = len(model_results['tasks'])
            results_summary.append(model_results)

            log(f"\n  📊 TOTALE: {total_s:.0f}s | Score medio: {avg_score:.3f} | OK: {ok_count}/{len(model_results['tasks'])}")

            unload(m['name'])

    # ---- CLASSIFICA FINALE ----
    results_summary.sort(key=lambda x: (-x['avg_score'], x['total_s']))

    log(f"\n\n{'='*70}")
    log(f"🏆 CLASSIFICA FINALE — {len(results_summary)} modelli testati")
    log(f"{'='*70}")
    log(f"{'#':>3} {'Modello':<40} {'Score':>6} {'Tempo':>7} {'OK':>4} {'Tier':<6}")
    log(f"{'-'*70}")
    for i, r in enumerate(results_summary, 1):
        log(f"{i:>3} {r['model']:<40} {r['avg_score']:>6.3f} {r['total_s']:>6.0f}s {r['ok_count']:>3}/{r['total_tasks']:<2} {r['tier']:<6}")

    # salva classifica
    cls_path = os.path.join(HERE, 'results', f'classifica_realworld_{ts}.json')
    json.dump(results_summary, open(cls_path, 'w'), indent=2, ensure_ascii=False)
    log(f"\nClassifica salvata: {cls_path}")
    log(f"FINITO. {n_done} test completati.")


if __name__ == '__main__':
    main()
