#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera TUTTI i grafici dell'articolo dai dati giudicati + varianti. Robusto su dati mancanti."""
import json, glob, os, sys
from collections import defaultdict
HERE = os.path.dirname(os.path.abspath(__file__)); REP = os.path.join(HERE, 'report'); os.makedirs(REP, exist_ok=True)
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
ACC = '#e07b00'; GRY = '#888'; OK = '#22c55e'
def rd(p): return [json.loads(l) for l in open(p, encoding='utf-8') if l.strip()] if p and os.path.exists(p) else []
def latest(pat):
    fs = glob.glob(os.path.join(HERE, 'results', pat)); return max(fs, key=os.path.getmtime) if fs else None
def avg(x): return sum(x)/len(x) if x else 0
def jload(name):
    p = os.path.join(REP, name); return json.load(open(p)) if os.path.exists(p) else None

out = {}
# 1) classifica giudicata (gemma31)
rk = jload('ranking_gemma4_31b.json')
if rk:
    labs = [r['lab'] for r in rk]; sc = [r['score'] for r in rk]
    plt.figure(figsize=(9,5)); plt.barh(labs[::-1], sc[::-1], color=ACC)
    plt.xlabel('Punteggio qualità (0–1, giudice cieco)'); plt.title('Classifica GIUDICATA — qualità reale')
    plt.xlim(0,1); plt.tight_layout(); plt.savefig(f'{REP}/chart_judged.png', dpi=130); plt.close()
    out['judged'] = rk
# 2) cross-check: vincitore vs gemma31
others = [f for f in glob.glob(f'{REP}/ranking_*.json') if 'gemma4_31b' not in f]
if rk and others:
    rk2 = json.load(open(max(others, key=os.path.getmtime)))
    m1 = {r['lab']: r['score'] for r in rk}; m2 = {r['lab']: r['score'] for r in rk2}
    labs = [r['lab'] for r in rk]
    import numpy as np
    x = np.arange(len(labs)); w = 0.38
    plt.figure(figsize=(10,5))
    plt.bar(x-w/2, [m1.get(l,0) for l in labs], w, label='giudice gemma31', color=ACC)
    plt.bar(x+w/2, [m2.get(l,0) for l in labs], w, label='contro-giudice (vincitore)', color=GRY)
    plt.xticks(x, labs, rotation=35, ha='right', fontsize=8); plt.ylabel('Punteggio'); plt.legend()
    plt.title('Riprova: due giudici a confronto (robustezza)'); plt.tight_layout()
    plt.savefig(f'{REP}/chart_crosscheck.png', dpi=130); plt.close()
    out['crosscheck'] = rk2
# 3) velocità + quadrante (da merged)
merged = rd(latest('results_merged_*.jsonl'))
spd = defaultdict(list)
for r in merged:
    if r.get('ok') and r.get('tok_s'): spd[r.get('model_lab', r['model'])].append(r['tok_s'])
spd = {k: round(avg(v),1) for k,v in spd.items()}
if spd:
    labs = sorted(spd, key=lambda k:-spd[k])
    plt.figure(figsize=(9,5)); plt.barh(labs[::-1], [spd[l] for l in labs][::-1], color='#2f5d62')
    plt.xlabel('Velocità (token/s)'); plt.title('Velocità di generazione'); plt.tight_layout()
    plt.savefig(f'{REP}/chart_speed.png', dpi=130); plt.close()
    out['speed'] = spd
if rk and spd:
    plt.figure(figsize=(8.5,6))
    for r in rk:
        s = spd.get(r['lab'], 0)
        plt.scatter(s, r['score'], s=130, color=ACC)
        plt.annotate(r['lab'], (s, r['score']), fontsize=8, xytext=(5,4), textcoords='offset points')
    plt.xlabel('Velocità (token/s) →'); plt.ylabel('Qualità giudicata (0–1) →')
    plt.title('Quadrante qualità × velocità'); plt.grid(alpha=.2); plt.tight_layout()
    plt.savefig(f'{REP}/chart_quadrant.png', dpi=130); plt.close()
# 4) thinking on/off + caveman (da variants)
vr = rd(latest('results_variants_*.jsonl'))
def agg_mode(rows, mode):
    d = defaultdict(lambda: {'q':[], 'p':0, 'n':0, 's':[]})
    for r in rows:
        if r.get('mode')!=mode or not r.get('ok'): continue
        b = d[r.get('model_lab', r['model'])]; b['q'].append((r.get('check') or {}).get('score',0))
        b['p'] += 1 if (r.get('check') or {}).get('passed') else 0; b['n']+=1
        if r.get('tok_s'): b['s'].append(r['tok_s'])
    return {k:{'pass':round(v['p']/v['n'],2) if v['n'] else 0,'spd':round(avg(v['s']),1),'n':v['n']} for k,v in d.items()}
import numpy as np
toff, ton = agg_mode(vr,'think_off'), agg_mode(vr,'think_on')
common = [m for m in toff if m in ton]
if common:
    x = np.arange(len(common)); w=0.38
    plt.figure(figsize=(9,5))
    plt.bar(x-w/2, [toff[m]['pass'] for m in common], w, label='think OFF', color=OK)
    plt.bar(x+w/2, [ton[m]['pass'] for m in common], w, label='think ON', color=GRY)
    plt.xticks(x, common, rotation=20, ha='right', fontsize=8); plt.ylabel('Pass rate (correttezza formato)')
    plt.title('Thinking ON vs OFF — il ragionamento conviene?'); plt.legend(); plt.tight_layout()
    plt.savefig(f'{REP}/chart_thinking.png', dpi=130); plt.close()
    out['thinking'] = {'off':toff,'on':ton}
cav = agg_mode(vr,'caveman')
if cav: out['caveman'] = cav
json.dump(out, open(f'{REP}/data_final.json','w'), ensure_ascii=False, indent=2)
print("grafici fatti:", [f for f in os.listdir(REP) if f.endswith('.png')])
