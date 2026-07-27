#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Giudice REAL-WORLD — valuta le risposte del benchmark con gemma4:12b.
A differenza dei check automatici (keyword), il giudice valuta la QUALITÀ reale:
contenuto, completezza, correttezza, utilità pratica.

Uso: python3 judge_realworld.py [--judge gemma4:12b] [--file results/results_realworld_XXX.jsonl]
"""
import json, os, sys, glob, time, urllib.request, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
OLLAMA = "http://localhost:11434/api/generate"

JUDGE = 'gemma4:12b'
if '--judge' in sys.argv:
    JUDGE = sys.argv[sys.argv.index('--judge') + 1]

# Rubriche per task — cosa valuta il giudice
RUBRICHE = {
    'inv_find_bug': (
        "Analisi di sicurezza e logica su codice Flask con SQL injection.\n"
        "5=tiene tutti i bug (SQL injection, mancanza validazione, nessun controllo input), "
    "spiega il rischio di ognuno, propone fix concreto.\n"
    "4=tiene i bug principali ma ne manca qualcuno o fix generico.\n"
    "3=individua il problema principale ma spiegazione vaga.\n"
    "2=individua solo parte del problema.\n"
    "1=non trova bug o risposta generica/irrilevante."
    ),
    'diag_ev_system': (
        "Diagnosi di un veicolo EV con sintomo intermittente (si ferma e riparte, errore E-03).\n"
    "5=diagnosi sistematica con albero decisionale, test misurabili, causa probabilistica, "
    "soluzione concreta con pezzi/procedura.\n"
    "4=buona diagnosi ma manca un passaggio o la soluzione è vaga.\n"
    "3=individua la zona del problema ma non scende nel dettaglio.\n"
    "2=risposta generica 'controlla il BMS'.\n"
    "1=non diagnostica o risposta inutile."
    ),
    'create_dispensa': (
        "Dispensa pratica su BMS guasto per tecnici EV.\n"
    "5=strutturata (strumenti, procedura, errori comuni, quando chiedere aiuto), "
    "italiano semplice da officina, info corrette e utili.\n"
    "4=buona ma manca una sezione o info generiche.\n"
    "3=disorganizzata o troppo teorica.\n"
    "2=lista di parole senza struttura.\n"
    "1=irrilevante o vuota."
    ),
    'search_mosfet': (
        "Confronto tecnico tra MOSFET per controller EV (IRF3205 vs IRF1404 vs IRFZ44N).\n"
    "5=specifiche corrette (Vds, Id, Rds), prezzo realistico, pro/contro precisi, "
    "raccomandazione motivata per motorino 48V.\n"
    "4=specifiche corrette ma raccomandazione vaga.\n"
    "3=confronto generico senza numeri.\n"
    "2=nomi i MOSFET ma senza confronto.\n"
    "1=non sa di cosa si parla."
    ),
    'fix_injection': (
        "Fix di SQL injection su codice Flask.\n"
    "5=usa parametrized query (placeholders), spiega perché, non rompe la funzionalità, "
    "menziona altre sicurezze (validazione input).\n"
    "4=fix corretto ma spiegazione breve.\n"
    "3=fix parziale (es. solo escape, non parametrizzato).\n"
    "2=proposta errata o rompe il codice.\n"
    "1=non capisce il problema."
    ),
    'predict_batt_degrad': (
        "Predizione degradamento batteria Li-ion su bici elettrica 48V 20Ah, 300 cicli, Livorno.\n"
    "5=previsioni temporali concrete (mese X perdi Y% autonomia), cause specifiche "
    "(cicli, temperatura, stress), mitigazioni actionable (carica 80%, bilanciamento).\n"
    "4=buone previsioni ma meno dettagliate.\n"
    "3=generico 'la batteria degrada'.\n"
    "2=risposta vuota o errata.\n"
    "1=irrilevante."
    ),
    'multi_build_scooter': (
        "Piano completo conversione Piaggio Ciao → elettrico, budget 800€, 40km, 45km/h.\n"
    "5=componenti con prezzi realistici, fasi di lavoro ordinate, tempistiche, "
    "rischi identificati, cosa delegare vs fai-da-te, totale within budget.\n"
    "4=buon piano ma manca un aspetto (prezzi o tempistiche).\n"
    "3=elenco componenti senza piano.\n"
    "2=proposta irrealistica (prezzi sbagliati o componenti incompatibili).\n"
    "1=non risponde alla domanda."
    ),
    'code_battery_monitor': (
        "Script Python per monitoraggio batteria con ADS1115, SOC, LED, CSV.\n"
    "5=codice funzionante, gestione errori, ADS1115 corretto, curva SOC plausibile, "
    "LED con soglie, CSV con timestamp, imports corretti.\n"
    "4=codice buono ma manca un componente (es. gestione errori).\n"
    "3=codice parziale o con errori logici.\n"
    "2=codice non funzionante o troppo semplice.\n"
    "1=irrilevante."
    ),
    'search_tools': (
        "5 strumenti indispensabili per officina EV con marca, prezzo, dove comprarlo.\n"
    "5=strumenti giusti (multimetro, saldatore, ecc.), marche reali, prezzi "
    "realistici per Italia, negozi/link, spiegazione 'perché'.\n"
    "4=strumenti giusti ma prezzi vaghi.\n"
    "3=lista generica senza dettagli.\n"
    "2=strumenti sbagliati o fuori tema.\n"
    "1=irrilevante."
    ),
    'diag_comm_error': (
        "Diagnosi errore comunicazione display-sensore Hall (velocità erratiche).\n"
    "5=albero diagnostico completo (cavi, connettori, schermatura, firmware), "
    "test misurabili (oscilloscopio su Hall), soluzione graduale.\n"
    "4=buona diagnosi ma manca un test.\n"
    "3='controlla i cavi' senza dettagli.\n"
    "2=risposta generica.\n"
    "1=non diagnostica."
    ),
}

def judge_one(task_id, task_prompt, response):
    """Chiede a gemma4:12b di valutare la risposta (1-5)."""
    rub = RUBRICHE.get(task_id, "Valuta la qualità complessiva: correttezza, completezza, utilità.")
    resp = (response or '')[:4000]  # taglia risposte lunghissime
    prompt = (
        "Sei un valutatore severo e imparziale. NON sai quale modello ha prodotto la risposta.\n\n"
        f"COMPITO RICHIESTO:\n{task_prompt[:1500]}\n\n"
        f"RUBRICA SPECIFICA:\n{rub}\n\n"
        f"RISPOSTA DA VALUTARE:\n<<<\n{resp}\n>>>\n\n"
        "Dai un voto INTERO da 1 a 5 e una motivazione di max 100 caratteri.\n"
        'Rispondi SOLO JSON: {"voto":N,"perche":"..."}'
    )
    body = {
        'model': JUDGE, 'prompt': prompt, 'stream': False, 'think': False,
        'format': 'json', 'keep_alive': '30m',
        'options': {'temperature': 0.0, 'num_predict': 200}
    }
    data = json.dumps(body).encode()
    t0 = time.time()
    r = urllib.request.urlopen(urllib.request.Request(
        OLLAMA, data=data, headers={'Content-Type': 'application/json'}), timeout=300)
    out = json.loads(r.read()).get('response', '')
    wall = time.time() - t0
    try:
        d = json.loads(out)
        v = int(d.get('voto') or d.get('vote') or 0)
        return max(1, min(5, v)), str(d.get('perche', ''))[:100], round(wall, 1)
    except Exception:
        return 0, f'parse-fail: {out[:50]}', round(wall, 1)


def main():
    # trova il file più recente
    args = [a for a in sys.argv[1:] if not a.startswith('--') and a != JUDGE]
    if args:
        path = args[0]
    else:
        candidates = glob.glob(os.path.join(HERE, 'results', 'results_realworld_*.jsonl'))
        # escludi il test piccolo (_1254)
        candidates = [c for c in candidates if '_1254.jsonl' not in c]
        if not candidates:
            candidates = glob.glob(os.path.join(HERE, 'results', 'results_realworld_*.jsonl'))
        path = max(candidates, key=os.path.getmtime) if candidates else None

    if not path or not os.path.exists(path):
        print("Nessun file results_realworld trovato."); return

    # carica prompt originali dei task
    sys.path.insert(0, HERE)
    from bench_realworld import REAL_TASKS
    PROMPTS = {t['id']: t['prompt'] for t in REAL_TASKS}

    rows = [json.loads(l) for l in open(path, encoding='utf-8') if l.strip()]
    ts = datetime.datetime.now().strftime('%Y%m%d_%H%M')
    outp = os.path.join(HERE, 'results', f'judged_realworld_{ts}.jsonl')

    print(f"🧑‍⚖️ Giudice: {JUDGE}")
    print(f"📄 File: {os.path.basename(path)} ({len(rows)} risposte)")
    print(f"📝 Output: {outp}\n")

    from collections import defaultdict
    agg = defaultdict(lambda: {'pts': [], 'times': [], 'n': 0})

    with open(outp, 'w') as out:
        for i, r in enumerate(rows, 1):
            m = r.get('model', '?')
            tid = r.get('task', '?')
            prompt = PROMPTS.get(tid, r.get('prompt', ''))
            resp = r.get('response', '')

            if not r.get('ok'):
                voto, why, jwall = 0, 'errore/timeout', 0
                final = 0.0
                print(f"  [{i:>3}/{len(rows)}] {m:35s} {tid:22s} ❌ errore")
            else:
                voto, why, jwall = judge_one(tid, prompt, resp)
                final = round((voto - 1) / 4, 3) if voto else 0.0  # 1-5 → 0-1
                star = '⭐' * voto if voto else '?'
                print(f"  [{i:>3}/{len(rows)}] {m:35s} {tid:22s} {star} {voto}/5  {why[:50]}")

            agg[m]['pts'].append(final)
            agg[m]['times'].append(r.get('wall_s', 0))
            agg[m]['n'] += 1

            rec = {k: v for k, v in r.items() if k != 'response'}
            rec['judge_voto'] = voto
            rec['judge_why'] = why
            rec['judge_score'] = final
            rec['judge_time'] = jwall
            out.write(json.dumps(rec, ensure_ascii=False) + "\n")
            out.flush()

    # ---- CLASSIFICA FINALE ----
    def avg(x): return round(sum(x)/len(x), 3) if x else 0
    def avg_t(x): return round(sum(x)/len(x), 1) if x else 0

    rank = sorted(
        [(m, avg(a['pts']), avg_t(a['times']), a['n'],
          round(min(a['pts']),3) if a['pts'] else 0,
          round(max(a['pts']),3) if a['pts'] else 0)
         for m, a in agg.items()],
        key=lambda x: (-x[1], x[2])  # prima score, poi tempo
    )

    print(f"\n{'='*75}")
    print(f"🏆 CLASSIFICA GIUDICATA DA {JUDGE}")
    print(f"{'='*75}")
    print(f"{'#':>3} {'Modello':<38} {'Score':>6} {'Min':>5} {'Max':>5} {'Tempo':>7}")
    print(f"{'-'*75}")
    for i, (m, sc, t, n, mn, mx) in enumerate(rank, 1):
        bar = '█' * int(sc * 20)
        print(f"{i:>3} {m:<38} {sc:>6.3f} {mn:>5.2f} {mx:>5.2f} {t:>5.0f}s  {bar}")

    # salva classifica
    cls_path = os.path.join(HERE, 'results', f'classifica_giudicata_{ts}.json')
    json.dump([{'rank': i+1, 'model': m, 'judge_score': sc, 'judge_avg_voto': round(sc*4+1,1),
                'min': mn, 'max': mx, 'avg_time_s': t, 'n': n}
               for i, (m, sc, t, n, mn, mx) in enumerate(rank)],
              open(cls_path, 'w'), indent=2, ensure_ascii=False)

    # salva report markdown
    md_path = os.path.join(HERE, 'results', f'REPORT_GIUDICATO_{ts}.md')
    L = [
        f"# Classifica Giudicata — Benchmark Real-World",
        f"",
        f"**Giudice:** `{JUDGE}` (cieco, 1-5 → 0-1)",
        f"**File:** `{os.path.basename(path)}` ({len(rows)} risposte)",
        f"**Data:** {datetime.datetime.now():%Y-%m-%d %H:%M}",
        f"",
        f"## Classifica",
        f"",
        f"| # | Modello | Score | Voto medio | Min | Max | Tempo |",
        f"|---|---------|-------|-----------|-----|-----|-------|",
    ]
    for i, (m, sc, t, n, mn, mx) in enumerate(rank, 1):
        voto_medio = round(sc * 4 + 1, 1)
        L.append(f"| {i} | {m} | **{sc:.3f}** | {voto_medio}/5 | {mn:.2f} | {mx:.2f} | {t:.0f}s |")

    L += [
        "",
        "## Top 4 per Categoria",
        ""
    ]

    # top 4 per categoria
    cat_models = defaultdict(lambda: defaultdict(list))
    for r in rows:
        if r.get('ok'):
            cat_models[r.get('cat', '?')][r['model']].append(r.get('judge_score', 0))

    cat_names = {
        'investigate': '🔍 Indagine Codice', 'diagnose': '🩺 Diagnosi Tecnica',
        'create': '📝 Creazione Contenuto', 'search': '🔬 Ricerca Tecnica',
        'fix': '🔒 Fix Sicurezza', 'predict': '🔮 Predizione Problemi',
        'multi_step': '📋 Compito Multi-Fase'
    }

    for cat in ['investigate','diagnose','create','search','fix','predict','multi_step']:
        if cat not in cat_models: continue
        ranked = sorted(
            [(m, sum(s)/len(s)) for m, s in cat_models[cat].items()],
            key=lambda x: -x[1]
        )[:4]
        L.append(f"### {cat_names.get(cat, cat)}")
        L.append(f"| # | Modello | Score |")
        L.append(f"|---|---------|-------|")
        for i, (m, sc) in enumerate(ranked, 1):
            L.append(f"| {i} | {m} | {sc:.3f} |")
        L.append("")

    with open(md_path, 'w') as f:
        f.write("\n".join(L))

    print(f"\n📁 Salvato:")
    print(f"   {outp}")
    print(f"   {cls_path}")
    print(f"   {md_path}")


if __name__ == '__main__':
    main()
