#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Giudice v2 — valuta risposte SENZA penalizzare troncamento.
Valuta solo CORRETTEZZA di quello che c'è, non incompletezza.
"""
import json, os, sys, glob, time, urllib.request, datetime
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
OLLAMA = "http://localhost:11434/api/generate"

JUDGE = 'gemma4:26b'
if '--judge' in sys.argv:
    JUDGE = sys.argv[sys.argv.index('--judge') + 1]

# Trova file results v2
def find_results():
    args = [a for a in sys.argv[1:] if not a.startswith('--') and a != JUDGE]
    if args:
        return args[0]
    candidates = glob.glob(os.path.join(HERE, 'results', 'bench_v2_*.jsonl'))
    if not candidates:
        candidates = glob.glob(os.path.join(HERE, 'results', 'results_realworld_*.jsonl'))
    return max(candidates, key=os.path.getmtime) if candidates else None

# Rubriche adattate — focuses su correttezza, non completezza
RUBRICHE = {
    'inv_find_bug': (
        "Analisi di sicurezza su codice Flask con SQL injection.\n"
        "Valuta la CORRETTEZZA di quello che c'è:\n"
        "- Se trova la SQL injection → +2 punti\n"
        "- Se spiega il rischio → +1 punto\n"
        "- Se propone un fix → +1 punto\n"
        "- Se trova altri problemi → +1 punto bonus\n"
        "NON penalizzare se la risposta è troncata. Valuta solo ciò che è stato scritto."
    ),
    'diag_ev_system': (
        "Diagnosi veicolo EV con sintomo intermittente.\n"
        "Valuta la CORRETTEZZA:\n"
        "- Diagnosi logica e sistematica → +2 punti\n"
        "- Test misurabili proposti → +1 punto\n"
        "- Causa identificata correttamente → +1 punto\n"
        "- Soluzione concreta → +1 punto\n"
        "NON penalizzare troncamenti."
    ),
    'create_dispensa': (
        "Dispensa pratica su BMS guasto.\n"
        "Valuta la QUALITÀ del contenuto scritto:\n"
        "- Struttura chiara → +1 punto\n"
        "- Contenuto corretto e utile → +2 punti\n"
        "- Linguaggio semplice da officina → +1 punto\n"
        "- Elenchi puntati e organizzazione → +1 punto\n"
        "NON penalizzare se è più corta del previsto."
    ),
    'search_mosfet': (
        "Confronto MOSFET per controller EV.\n"
        "Valuta la CORRETTEZZA tecnica:\n"
        "- Specifiche corrette (Vds, Id, Rds) → +2 punti\n"
        "- Confronto utile → +1 punto\n"
        "- Raccomandazione motivata → +1 punto\n"
        "- Prezzi realistici → +1 punto bonus\n"
        "NON penalizzare troncamenti."
    ),
    'fix_injection': (
        "Fix di SQL injection su codice Flask.\n"
        "Valuta la CORRETTEZZA della soluzione:\n"
        "- Usa parametrized query → +3 punti\n"
        "- Spiega perché → +1 punto\n"
        "- Non rompe la funzionalità → +1 punto\n"
        "NON penalizzare troncamenti."
    ),
    'predict_batt_degrad': (
        "Predizione degradamento batteria Li-ion.\n"
        "Valuta la QUALITÀ delle previsioni:\n"
        "- Previsioni concrete con tempistiche → +2 punti\n"
        "- Cause specifiche → +1 punto\n"
        "- Mitigazioni actionable → +1 punto\n"
        "- Consigli pratici → +1 punto\n"
        "NON penalizzare troncamenti."
    ),
    'multi_build_scooter': (
        "Piano conversione Piaggio Ciao → elettrico.\n"
        "Valuta la QUALITÀ del piano:\n"
        "- Componenti con prezzi realistici → +2 punti\n"
        "- Fasi di lavoro ordinate → +1 punto\n"
        "- Budget rispettato → +1 punto\n"
        "- Rischi identificati → +1 punto\n"
        "NON penalizzare troncamenti."
    ),
    'code_battery_monitor': (
        "Script Python per monitoraggio batteria.\n"
        "Valuta la QUALITÀ del codice:\n"
        "- Codice funzionante e ben strutturato → +2 punti\n"
        "- Gestione errori → +1 punto\n"
        "- ADS1115 corretto → +1 punto\n"
        "- CSV con timestamp → +1 punto\n"
        "NON penalizzare se manca qualche parte."
    ),
    'search_tools': (
        "5 strumenti indispensabili per officina EV.\n"
        "Valuta la QUALITÀ degli strumenti elencati:\n"
        "- Strumenti giusti e pertinenti → +2 punti\n"
        "- Marche e modelli reali → +1 punto\n"
        "- Prezzi realistici → +1 punto\n"
        "- Spiegazione 'perché' → +1 punto\n"
        "NON penalizzare troncamenti."
    ),
    'diag_comm_error': (
        "Diagnosi errore comunicazione display-sensore Hall.\n"
        "Valuta la CORRETTEZZA della diagnosi:\n"
        "- Albero diagnostico logico → +2 punti\n"
        "- Test misurabili → +1 punto\n"
        "- Soluzione graduale → +1 punto\n"
        "- Causa identificata → +1 punto\n"
        "NON penalizzare troncamenti."
    ),
}

def judge_one(task_id, task_prompt, response):
    rub = RUBRICHE.get(task_id, "Valuta la qualità complessiva della risposta.")
    resp = (response or '')[:4000]
    trunc_note = ""
    if response and not response.rstrip().endswith(('.', '!', '?', '>', '`', '}', ']')):
        trunc_note = "\n\n⚠️ NOTA: La risposta potrebbe essere troncata. Valuta SOLO il contenuto presente, NON penalizzare per ciò che manca."
    
    prompt = (
        "Sei un valutatore severo e imparziale. NON sai quale modello ha prodotto la risposta.\n"
        "IMPORTANTE: Valuta la QUALITÀ e CORRETTEZZA di quello che c'è. NON penalizzare se la risposta è troncata.\n"
        f"{trunc_note}\n\n"
        f"COMPITO RICHIESTO:\n{task_prompt[:1500]}\n\n"
        f"RUBRICA SPECIFICA:\n{rub}\n\n"
        f"RISPOSTA DA VALUTARE:\n<<<\n{resp}\n>>>\n\n"
        "Dai un voto INTERO da 1 a 5 e una motivazione di max 100 caratteri.\n"
        "Rispondi SOLO JSON: {\"voto\":N,\"perche\":\"...\"}"
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
    path = find_results()
    if not path or not os.path.exists(path):
        print("Nessun file results trovato."); return

    sys.path.insert(0, HERE)
    from tasks_realworld import REAL_TASKS
    PROMPTS = {t['id']: t['prompt'] for t in REAL_TASKS}

    rows = [json.loads(l) for l in open(path, encoding='utf-8') if l.strip()]
    ts = datetime.datetime.now().strftime('%Y%m%d_%H%M')
    outp = os.path.join(HERE, 'results', f'judged_v2_{ts}.jsonl')

    print(f"🧑‍⚖️ Giudice: {JUDGE}")
    print(f"📄 File: {os.path.basename(path)} ({len(rows)} risposte)")
    print(f"📝 Output: {outp}\n")

    agg = defaultdict(lambda: {'pts': [], 'times': [], 'n': 0})

    with open(outp, 'w') as out:
        for i, r in enumerate(rows, 1):
            m = r.get('model', '?')
            tid = r.get('task', '?')
            prompt = PROMPTS.get(tid, r.get('prompt', ''))
            resp = r.get('response', '')

            ok = r.get('ok', bool(resp))
            if not ok:
                voto, why, jwall = 0, 'errore/timeout', 0
                final = 0.0
                print(f"  [{i:>3}/{len(rows)}] {m:50s} {tid:22s} ❌ errore")
            else:
                voto, why, jwall = judge_one(tid, prompt, resp)
                final = round((voto - 1) / 4, 3) if voto else 0.0
                star = '⭐' * voto if voto else '?'
                trunc = '📎' if resp and not resp.rstrip().endswith(('.', '!', '?', '>', '`', '}', ']')) else '  '
                print(f"  [{i:>3}/{len(rows)}] {m:50s} {tid:22s} {star} {voto}/5 {trunc} {why[:40]}")

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

    def avg(x): return round(sum(x)/len(x), 3) if x else 0
    def avg_t(x): return round(sum(x)/len(x), 1) if x else 0

    rank = sorted(
        [(m, avg(a['pts']), avg_t(a['times']), a['n'],
          round(min(a['pts']),3) if a['pts'] else 0,
          round(max(a['pts']),3) if a['pts'] else 0)
         for m, a in agg.items()],
        key=lambda x: (-x[1], x[2])
    )

    print(f"\n{'='*80}")
    print(f"🏆 CLASSIFICA — Giudice: {JUDGE} (senza penalità troncamento)")
    print(f"{'='*80}")
    print(f"{'#':>3} {'Modello':<50} {'Score':>6} {'Min':>5} {'Max':>5} {'Tempo':>7}")
    print(f"{'-'*80}")
    for i, (m, sc, t, n, mn, mx) in enumerate(rank, 1):
        bar = '█' * int(sc * 20)
        print(f"{i:>3} {m:<50} {sc:>6.3f} {mn:>5.2f} {mx:>5.2f} {t:>5.0f}s  {bar}")

    cls_path = os.path.join(HERE, 'results', f'classifica_v2_{ts}.json')
    json.dump([{'rank': i+1, 'model': m, 'judge_score': sc, 'judge_avg_voto': round(sc*4+1,1),
                'min': mn, 'max': mx, 'avg_time_s': t, 'n': n}
               for i, (m, sc, t, n, mn, mx) in enumerate(rank)],
              open(cls_path, 'w'), indent=2, ensure_ascii=False)

    md_path = os.path.join(HERE, 'results', f'REPORT_V2_{ts}.md')
    L = [
        f"# Classifica Benchmark v2 — Senza Penalità Troncamento",
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

    with open(md_path, 'w') as f:
        f.write("\n".join(L))

    print(f"\n📁 Salvato:")
    print(f"   {outp}")
    print(f"   {cls_path}")
    print(f"   {md_path}")

if __name__ == '__main__':
    main()
