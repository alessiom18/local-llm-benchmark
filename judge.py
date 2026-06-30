#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GIUDICE di qualità — ri-valuta gli output GIÀ SALVATI (nessun re-run dei modelli).
Metodologia a due livelli:
  - task OGGETTIVI (classify/extract/config/code endpoint): resta il check automatico (correttezza di forma).
  - task APERTI (strategy/recipe/code_review/copy/website): un MODELLO GIUDICE forte assegna un voto 1-5
    ALLA CIECA (non sa quale modello ha prodotto la risposta), con rubrica per categoria.
Output: results/judged_<ts>.jsonl + report/ranking_giudicato.md
Giudice di default: gemma4:31b (forte, locale). Caveat: gemma giudica anche gemma → bias dichiarato.
Uso: python3 judge.py [results/results_XXXX.jsonl] [--judge gemma4:31b]
"""
import json, os, sys, glob, time, urllib.request, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
OLLAMA = "http://localhost:11434/api/generate"

JUDGE = 'gemma4:31b'
if '--judge' in sys.argv:
    JUDGE = sys.argv[sys.argv.index('--judge') + 1]

OPEN_CATS = {'strategy', 'recipe', 'code', 'copy', 'website'}  # code_review è cat 'code' ma expects text
RUBRICHE = {
    'strategy': "Valuti un consiglio commerciale a un piccolo negozio. 5=concreto, specifico, attuabile subito, contestuale; 1=generico, vago, ovvio o fuori tema.",
    'recipe':   "Valuti una ricetta. 5=ingredienti con quantità + procedimento chiaro a passi, coerente coi vincoli (es. vegana/senza glutine); 1=incompleta o sbagliata.",
    'code':     "Valuti codice o una review di codice. 5=corretto, sicuro, completo, idiomatico; 1=errato, insicuro o irrilevante.",
    'copy':     "Valuti un testo di marketing breve per un menu. 5=invitante, sintetico, rispetta il limite di lunghezza richiesto; 1=prolisso, piatto o fuori lunghezza.",
    'website':  "Valuti il CODICE HTML di un sito vetrina. 5=pagina completa e ben strutturata (sezioni richieste, CTA, CSS curato, chiusa correttamente); 1=incompleta, troncata o povera.",
}

def judge_one(task_prompt, cat, response):
    rub = RUBRICHE.get(cat, "Valuta la qualità complessiva.")
    resp = (response or '')[:4000]
    prompt = (
        "Sei un valutatore severo e imparziale. NON sai quale modello ha prodotto la risposta.\n"
        f"COMPITO RICHIESTO: {task_prompt}\n\n"
        f"RUBRICA: {rub}\n\n"
        f"RISPOSTA DA VALUTARE:\n<<<\n{resp}\n>>>\n\n"
        'Dai un voto INTERO da 1 a 5 e una motivazione di una riga. Rispondi SOLO JSON: {"voto":N,"perche":"..."}.')
    body = {'model': JUDGE, 'prompt': prompt, 'stream': False, 'think': False,
            'format': 'json', 'keep_alive': '30m', 'options': {'temperature': 0.0, 'num_predict': 160}}
    r = urllib.request.urlopen(urllib.request.Request(
        OLLAMA, data=json.dumps(body).encode(), headers={'Content-Type': 'application/json'}), timeout=600)
    out = json.loads(r.read()).get('response', '')
    try:
        d = json.loads(out)
        v = int(d.get('voto') or d.get('vote') or 0)
        return max(1, min(5, v)), str(d.get('perche', ''))[:160]
    except Exception:
        return 0, 'parse-fail'

def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--') and a != JUDGE]
    path = args[0] if args else max(glob.glob(os.path.join(HERE, 'results', 'results_*.jsonl')), key=os.path.getmtime)
    # carico i prompt dei task per darli al giudice
    sys.path.insert(0, HERE)
    from tasks import TASKS
    PROMPT = {t['id']: t['prompt'] for t in TASKS}

    rows = [json.loads(l) for l in open(path, encoding='utf-8') if l.strip()]
    ts = datetime.datetime.now().strftime('%Y%m%d_%H%M')
    outp = os.path.join(HERE, 'results', f'judged_{ts}.jsonl')
    from collections import defaultdict
    agg = defaultdict(lambda: {'pts': [], 'lab': ''})

    print(f"giudice: {JUDGE} · file: {os.path.basename(path)}")
    with open(outp, 'w') as out:
        for r in rows:
            lab = r.get('model_lab', r.get('model'))
            agg[r['model']]['lab'] = lab
            rec = dict(r); rec.pop('response', None)
            if not r.get('ok'):
                rec['final'] = 0.0; rec['judge_note'] = 'errore/timeout'
            elif r['cat'] in OPEN_CATS:
                try:
                    v, why = judge_one(PROMPT.get(r['task'], r['task']), r['cat'], r.get('response'))
                    rec['voto'] = v; rec['judge_note'] = why
                    rec['final'] = round((v - 1) / 4, 3) if v else 0.0  # 1-5 → 0-1
                    print(f"  {lab:30s} {r['task']:18s} voto {v}/5  {why[:60]}")
                except Exception as e:
                    rec['final'] = None; rec['judge_note'] = f'judge-err {str(e)[:40]}'
                    print(f"  {lab:30s} {r['task']:18s} JUDGE ERR {str(e)[:40]}")
            else:
                # oggettivo: tengo il check automatico
                rec['final'] = (r.get('check') or {}).get('score', 0.0)
            if rec.get('final') is not None:
                agg[r['model']]['pts'].append(rec['final'])
            out.write(json.dumps(rec, ensure_ascii=False) + "\n"); out.flush()

    def avg(x): return round(sum(x)/len(x), 3) if x else 0
    rank = sorted(([a['lab'], avg(a['pts']), len(a['pts'])] for a in agg.values()), key=lambda x: -x[1])
    jslug = JUDGE.split('/')[-1].replace(':', '_')
    L = ["# Classifica GIUDICATA (qualità reale)", "",
         f"Giudice: `{JUDGE}` (cieco) · task aperti = voto 1-5 → 0-1; task oggettivi = check automatico.", "",
         "| # | Modello | Punteggio | n |", "|---|---------|-----------|---|"]
    for i, (lab, sc, n) in enumerate(rank, 1):
        L.append(f"| {i} | {lab} | **{sc}** | {n} |")
    open(os.path.join(HERE, 'report', f'ranking_{jslug}.md'), 'w').write("\n".join(L))
    json.dump([{'lab': lab, 'score': sc, 'n': n} for lab, sc, n in rank],
              open(os.path.join(HERE, 'report', f'ranking_{jslug}.json'), 'w'), ensure_ascii=False, indent=2)
    print("\n=== CLASSIFICA GIUDICATA ===")
    for i, (lab, sc, n) in enumerate(rank, 1):
        print(f"  {i}. {sc:.3f}  {lab}")
    print(f"\nsalvato: {outp} + report/ranking_giudicato.md")

if __name__ == '__main__':
    main()
