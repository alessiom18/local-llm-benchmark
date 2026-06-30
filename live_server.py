#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Server LIVE pipeline-aware: step, progresso, classifica live (clean) + giudicata. Stdlib."""
import json, os, glob, sys, re
from collections import defaultdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
HERE = os.path.dirname(os.path.abspath(__file__))
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8899
def _read(p):
    out = []
    if p and os.path.exists(p):
        for l in open(p, encoding='utf-8'):
            l = l.strip()
            if l:
                try: out.append(json.loads(l))
                except Exception: pass
    return out
def latest(pat, excl=()):
    fs = [f for f in glob.glob(os.path.join(HERE, 'results', pat)) if not any(e in f for e in excl)]
    return max(fs, key=os.path.getmtime) if fs else None
def avg(x): return round(sum(x)/len(x), 3) if x else 0

STEP_DEFS = [("STEP 1", "Aperti puliti"), ("STEP 2", "Varianti (thinking/caveman)"),
             ("STEP 3", "Merge dati"), ("STEP 4", "Giudice (gemma31)"), ("STEP 5", "Il vincitore rigiudica")]

def pipeline_state():
    log = os.path.join(HERE, 'results', 'master.log')
    txt = open(log, encoding='utf-8').read() if os.path.exists(log) else ''
    finished = 'MASTER FINITO' in txt
    cur = -1
    for i, (tag, _) in enumerate(STEP_DEFS):
        if tag in txt: cur = i
    steps = []
    for i, (tag, name) in enumerate(STEP_DEFS):
        steps.append({'name': name, 'done': (i < cur) or finished, 'current': (i == cur) and not finished})
    # ultima attività (riga modello/test) + vincitore
    model_now = ''
    for line in reversed(txt.splitlines()):
        m = re.search(r'=== (.+?) ===', line)
        if m and 'STEP' not in line: model_now = m.group(1); break
    win = ''
    mw = re.findall(r'VINCITORE.*?: (.+?) \(', txt)
    if mw: win = mw[-1]
    return {'steps': steps, 'finished': finished, 'model_now': model_now, 'winner': win,
            'phase': (STEP_DEFS[cur][1] if cur >= 0 else 'avvio') if not finished else 'COMPLETATO'}

def agg_by_model(rows):
    by = defaultdict(lambda: {'q': [], 's': [], 'n': 0, 'pass': 0, 'lab': '', 'tier': ''})
    for r in rows:
        if not r.get('ok'): continue
        b = by[r['model']]; b['lab'] = r.get('model_lab', r['model']); b['tier'] = r.get('tier', '')
        b['q'].append((r.get('check') or {}).get('score', 0))
        b['pass'] += 1 if (r.get('check') or {}).get('passed') else 0
        if r.get('tok_s'): b['s'].append(r['tok_s'])
        b['n'] += 1
    out = [{'lab': b['lab'], 'tier': b['tier'], 'q': avg(b['q']),
            'pass': round(b['pass']/b['n'], 2) if b['n'] else 0, 'spd': avg(b['s']), 'n': b['n']} for b in by.values()]
    out.sort(key=lambda x: -x['q']); return out

def build():
    pipe = pipeline_state()
    openf = latest('results_open_*.jsonl'); orows = _read(openf)
    # classifica giudicata, se presente
    judged = None; jfile = None
    for jf in sorted(glob.glob(os.path.join(HERE, 'report', 'ranking_*.json')), key=os.path.getmtime, reverse=True):
        try: judged = json.load(open(jf)); jfile = os.path.basename(jf); break
        except Exception: pass
    # varianti SOLO se step>=2 (evita lo stale del run killato)
    variants = []
    if any(s['name'].startswith('Varianti') and (s['done'] or s['current']) for s in pipe['steps']):
        vr = _read(latest('results_variants_*.jsonl'))
        va = defaultdict(lambda: {'q': [], 's': [], 'n': 0, 'pass': 0, 'lab': '', 'mode': ''})
        for r in vr:
            if not r.get('ok'): continue
            k = (r.get('model_lab', r['model']), r.get('mode', '?')); b = va[k]; b['lab'], b['mode'] = k
            b['q'].append((r.get('check') or {}).get('score', 0)); b['pass'] += 1 if (r.get('check') or {}).get('passed') else 0
            if r.get('tok_s'): b['s'].append(r['tok_s'])
            b['n'] += 1
        variants = sorted([{'lab': b['lab'], 'mode': b['mode'], 'q': avg(b['q']),
                            'pass': round(b['pass']/b['n'], 2) if b['n'] else 0, 'spd': avg(b['s']), 'n': b['n']} for b in va.values()],
                          key=lambda x: (x['lab'], x['mode']))
    newest = latest('results_*.jsonl')
    feed = _read(newest)
    recent = [{'model': r.get('model_lab', r['model']), 'task': r['task'], 'cat': r['cat'], 'mode': r.get('mode', ''),
               'ok': r.get('ok'), 'score': (r.get('check') or {}).get('score'), 'passed': (r.get('check') or {}).get('passed'),
               'wall': r.get('wall_s'), 'tok_s': r.get('tok_s')} for r in feed[-16:][::-1]]
    return {'pipeline': pipe, 'clean_done': len(orows), 'clean_planned': 72,
            'clean_ranking': agg_by_model(orows), 'variants': variants,
            'judged': judged, 'judge_file': jfile, 'recent': recent}

PAGE = """<!doctype html><html lang=it><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>Benchmark LIVE · SudoWAI</title><style>
:root{--bg:#0e1116;--card:#171b22;--line:#262b34;--txt:#e6e9ef;--mut:#8b93a1;--acc:#e07b00;--ok:#22c55e;--no:#ef4444}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--txt);font:15px/1.5 system-ui,Segoe UI,Roboto,sans-serif}
.wrap{max-width:1000px;margin:0 auto;padding:18px 16px 60px}h1{font-size:21px;margin:0 0 2px}
.sub{color:var(--mut);font-size:13px;margin:0 0 14px}.live{color:var(--ok);font-weight:700}
.steps{display:flex;gap:8px;flex-wrap:wrap;margin:8px 0 14px}
.step{flex:1;min-width:150px;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:9px 12px;font-size:12.5px}
.step.done{border-color:var(--ok)}.step.cur{border-color:var(--acc);box-shadow:0 0 0 1px var(--acc)}
.step .s{font-size:18px}.step .n{color:var(--mut);font-size:11px}
.bar{height:9px;background:#0a0d11;border:1px solid var(--line);border-radius:6px;overflow:hidden;margin:6px 0 4px}
.fill{height:100%;background:linear-gradient(90deg,#f5aa14,#c2410c);width:0;transition:width .5s}
h2{font-size:15px;margin:20px 0 8px;color:var(--mut)}
table{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--line);border-radius:11px;overflow:hidden}
th,td{padding:8px 11px;text-align:left;border-bottom:1px solid var(--line);font-size:13px}
th{color:var(--mut);font-size:11px;text-transform:uppercase}tr:last-child td{border-bottom:0}
.qbar{display:inline-block;height:8px;border-radius:4px;background:var(--acc);margin-left:6px;vertical-align:middle}
.tier{font-size:10px;padding:1px 6px;border-radius:5px;background:#30363d;color:var(--mut)}.tier.light{background:rgba(34,197,94,.15);color:var(--ok)}
.row{display:flex;gap:10px;align-items:center;padding:6px 10px;border-bottom:1px solid var(--line);font-size:12.5px}
.dot{width:8px;height:8px;border-radius:50%;flex:none}.dot.ok{background:var(--ok)}.dot.no{background:var(--no)}
.mono{font-family:ui-monospace,monospace;color:var(--mut);font-size:12px}.pill{margin-left:auto;font-size:11px;color:var(--mut)}
.badge{display:inline-block;background:rgba(224,123,0,.15);color:var(--acc);border:1px solid var(--acc);border-radius:6px;padding:2px 9px;font-size:12px;font-weight:700}
</style></head><body><div class=wrap>
<h1>🧪 Benchmark LIVE <span class=live id=phase></span></h1>
<p class=sub>«Non esiste il modello migliore» · pipeline a 5 step · <span id=now class=mono></span></p>
<div class=steps id=steps></div>
<h2>Avanzamento "aperti puliti" <span id=cprog class=mono></span></h2>
<div class=bar><div class=fill id=fill></div></div>
<div id=winwrap style=display:none;margin:10px 0><span class=badge id=winner></span></div>
<h2 id=jtitle>Classifica <span id=jsub class=mono></span></h2>
<table><thead><tr><th>#</th><th>Modello</th><th>Tier</th><th id=col4>Qualità</th><th id=col5>Pass</th><th>Tok/s</th><th>Test</th></tr></thead><tbody id=tb></tbody></table>
<div id=varwrap style=display:none><h2>🧪 Varianti — Thinking ON/OFF &amp; Caveman</h2>
<table><thead><tr><th>Modello</th><th>Modalità</th><th>Qualità</th><th>Pass</th><th>Tok/s</th><th>Test</th></tr></thead><tbody id=vtb></tbody></table></div>
<h2>Ultimi test</h2><div id=feed></div>
</div><script>
async function tick(){try{
 const d=await(await fetch('/api?'+Date.now())).json();const p=d.pipeline;
 document.getElementById('phase').textContent=p.finished?'● COMPLETATO':'● '+p.phase;
 document.getElementById('now').textContent=p.model_now?('in lavorazione: '+p.model_now):'';
 const st=document.getElementById('steps');st.innerHTML='';
 p.steps.forEach((s,i)=>{const e=document.createElement('div');e.className='step'+(s.done?' done':'')+(s.current?' cur':'');
  e.innerHTML='<div class=s>'+(s.done?'✅':(s.current?'⏳':'⚪'))+'</div><b>'+(i+1)+'. '+s.name+'</b>';st.appendChild(e);});
 document.getElementById('cprog').textContent=d.clean_done+' / '+d.clean_planned;
 document.getElementById('fill').style.width=Math.min(100,Math.round(100*d.clean_done/d.clean_planned))+'%';
 if(p.winner){document.getElementById('winwrap').style.display='block';document.getElementById('winner').textContent='🏆 Vincitore (giudice): '+p.winner;}
 // classifica: giudicata se c'è, sennò clean (auto-check)
 const tb=document.getElementById('tb');tb.innerHTML='';
 if(d.judged){document.getElementById('jtitle').firstChild.textContent='Classifica GIUDICATA ';
  document.getElementById('jsub').textContent='('+(d.judge_file||'')+')';document.getElementById('col4').textContent='Punteggio';document.getElementById('col5').textContent='';
  d.judged.forEach((m,i)=>{const tr=document.createElement('tr');
   tr.innerHTML='<td>'+(i+1)+'</td><td><b>'+m.lab+'</b></td><td></td><td><b>'+m.score.toFixed(2)+'</b><span class=qbar style="width:'+(m.score*70)+'px"></span></td><td></td><td></td><td>'+m.n+'</td>';tb.appendChild(tr);});
 }else{document.getElementById('jtitle').firstChild.textContent='Classifica provvisoria (dati puliti, check automatico) ';
  document.getElementById('jsub').textContent='— la qualità VERA arriva col giudice (step 4-5)';
  d.clean_ranking.forEach((m,i)=>{const tr=document.createElement('tr');
   tr.innerHTML='<td>'+(i+1)+'</td><td><b>'+m.lab+'</b></td><td><span class="tier '+m.tier+'">'+m.tier+'</span></td>'+
    '<td>'+m.q.toFixed(2)+'<span class=qbar style="width:'+(m.q*60)+'px"></span></td><td>'+Math.round(m.pass*100)+'%</td><td>'+m.spd+'</td><td>'+m.n+'</td>';tb.appendChild(tr);});}
 // varianti
 const vw=document.getElementById('varwrap');
 if(d.variants&&d.variants.length){vw.style.display='block';const vtb=document.getElementById('vtb');vtb.innerHTML='';
  const M={think_off:'🧠 think OFF',think_on:'💭 think ON',caveman:'🪨 caveman'};
  d.variants.forEach(v=>{const tr=document.createElement('tr');
   tr.innerHTML='<td><b>'+v.lab+'</b></td><td>'+(M[v.mode]||v.mode)+'</td><td>'+v.q.toFixed(2)+'</td><td>'+Math.round(v.pass*100)+'%</td><td>'+v.spd+'</td><td>'+v.n+'</td>';vtb.appendChild(tr);});}
 const f=document.getElementById('feed');f.innerHTML='';
 d.recent.forEach(r=>{const row=document.createElement('div');row.className='row';const ok=r.ok&&r.passed;
  row.innerHTML='<span class="dot '+(ok?'ok':'no')+'"></span><b>'+r.model+'</b><span class=mono>'+r.task+(r.mode?(' · '+r.mode):'')+'</span>'+
   '<span class=pill>'+(r.score!=null?('punti '+r.score):'—')+' · '+(r.wall||'?')+'s · '+(r.tok_s||'?')+'tk/s</span>';f.appendChild(row);});
}catch(e){document.getElementById('phase').textContent='● in attesa…';}}
tick();setInterval(tick,3000);
</script></body></html>"""

class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self):
        if self.path.startswith('/api'):
            b = json.dumps(build()).encode(); self.send_response(200)
            self.send_header('Content-Type', 'application/json'); self.send_header('Cache-Control', 'no-store')
            self.end_headers(); self.wfile.write(b)
        else:
            self.send_response(200); self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers(); self.wfile.write(PAGE.encode())

if __name__ == '__main__':
    print(f"live server :{PORT}"); ThreadingHTTPServer(('0.0.0.0', PORT), H).serve_forever()
