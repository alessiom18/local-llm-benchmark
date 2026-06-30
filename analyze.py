#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analizza i risultati del benchmark (results/results_*.jsonl) → tabelle markdown + grafici PNG + data.json.
Robusto su run PARZIALI. Genera:
  - report/summary.md        (classifica per modello + per categoria)
  - report/data.json         (per la pagina web / Chart.js)
  - report/chart_quality.png (qualità media per modello)
  - report/chart_speed.png   (velocità tok/s per modello)
  - report/chart_quadrant.png(qualità vs velocità — il "quadrante")
Uso: python3 analyze.py [results/results_XXXX.jsonl]   (default: il più recente)
"""
import json, os, sys, glob
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
REP = os.path.join(HERE, 'report'); os.makedirs(REP, exist_ok=True)

def load(path):
    rows = []
    for line in open(path, encoding='utf-8'):
        line = line.strip()
        if line:
            try: rows.append(json.loads(line))
            except Exception: pass
    return rows

def main():
    path = sys.argv[1] if len(sys.argv) > 1 else max(glob.glob(os.path.join(HERE, 'results', 'results_*.jsonl')), key=os.path.getmtime)
    rows = load(path)
    ok = [r for r in rows if r.get('ok')]
    print(f"caricati {len(rows)} record ({len(ok)} ok) da {os.path.basename(path)}")

    # aggregati per modello
    by_model = defaultdict(lambda: {'q': [], 'spd': [], 'n': 0, 'pass': 0, 'lab': '', 'tier': ''})
    by_model_cat = defaultdict(lambda: defaultdict(list))   # model -> cat -> [score]
    cats = set()
    for r in ok:
        m = r['model']; b = by_model[m]
        b['lab'] = r.get('model_lab', m); b['tier'] = r.get('tier', '')
        sc = (r.get('check') or {}).get('score', 0); b['q'].append(sc)
        b['pass'] += 1 if (r.get('check') or {}).get('passed') else 0
        if r.get('tok_s'): b['spd'].append(r['tok_s'])
        b['n'] += 1
        by_model_cat[m][r['cat']].append(sc)
        cats.add(r['cat'])

    def avg(x): return round(sum(x)/len(x), 3) if x else 0

    summary = []
    for m, b in by_model.items():
        summary.append({'model': m, 'lab': b['lab'], 'tier': b['tier'],
                        'quality': avg(b['q']), 'pass_rate': round(b['pass']/b['n'], 2) if b['n'] else 0,
                        'tok_s': avg(b['spd']), 'n': b['n']})
    summary.sort(key=lambda x: -x['quality'])

    # data.json (per la pagina web)
    data = {'source': os.path.basename(path), 'models': summary, 'categories': sorted(cats),
            'by_model_cat': {m: {c: avg(s) for c, s in cd.items()} for m, cd in by_model_cat.items()}}
    json.dump(data, open(os.path.join(REP, 'data.json'), 'w'), ensure_ascii=False, indent=2)

    # summary.md
    L = ["# Risultati benchmark — *non esiste il modello migliore*", "",
         f"Fonte: `{os.path.basename(path)}` · {len(ok)} test validi", "",
         "## Classifica per qualità media (check automatici, 0–1)", "",
         "| # | Modello | Tier | Qualità | Pass | Velocità (tok/s) | Test |",
         "|---|---------|------|---------|------|------------------|------|"]
    for i, s in enumerate(summary, 1):
        L.append(f"| {i} | {s['lab']} | {s['tier']} | **{s['quality']}** | {int(s['pass_rate']*100)}% | {s['tok_s']} | {s['n']} |")
    L += ["", "## Qualità per categoria (chi vince dove)", "",
          "| Modello | " + " | ".join(sorted(cats)) + " |",
          "|" + "---|" * (len(cats)+1)]
    for m, cd in sorted(by_model_cat.items(), key=lambda kv: -avg([v for vs in kv[1].values() for v in vs])):
        row = [by_model[m]['lab']] + [str(avg(cd.get(c, []))) for c in sorted(cats)]
        L.append("| " + " | ".join(row) + " |")
    L += ["", "> Tesi: nessun modello domina ovunque; un setup contenuto e ben instradato batte i giganti su molti task reali."]
    open(os.path.join(REP, 'summary.md'), 'w', encoding='utf-8').write("\n".join(L))

    # grafici
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        ACC = '#e07b00'
        labs = [s['lab'] for s in summary]
        # qualità
        plt.figure(figsize=(9, 5)); plt.barh(labs[::-1], [s['quality'] for s in summary][::-1], color=ACC)
        plt.xlabel('Qualità media (0–1)'); plt.title('Qualità media per modello'); plt.tight_layout()
        plt.savefig(os.path.join(REP, 'chart_quality.png'), dpi=130); plt.close()
        # velocità
        plt.figure(figsize=(9, 5)); plt.barh(labs[::-1], [s['tok_s'] for s in summary][::-1], color='#2f5d62')
        plt.xlabel('Velocità (token/s)'); plt.title('Velocità di generazione per modello'); plt.tight_layout()
        plt.savefig(os.path.join(REP, 'chart_speed.png'), dpi=130); plt.close()
        # quadrante qualità vs velocità
        plt.figure(figsize=(8, 6))
        for s in summary:
            plt.scatter(s['tok_s'], s['quality'], s=120, color=ACC if s['tier']=='light' else '#888')
            plt.annotate(s['lab'], (s['tok_s'], s['quality']), fontsize=8, xytext=(5,5), textcoords='offset points')
        plt.xlabel('Velocità (token/s) →  più veloce'); plt.ylabel('Qualità (0–1) →  meglio')
        plt.title('Quadrante: qualità vs velocità (arancio = gira in GPU)'); plt.grid(alpha=.2); plt.tight_layout()
        plt.savefig(os.path.join(REP, 'chart_quadrant.png'), dpi=130); plt.close()
        print("grafici salvati in report/")
    except Exception as e:
        print("grafici saltati:", e)

    print("FATTO. report/summary.md + data.json + grafici")

if __name__ == '__main__':
    main()
