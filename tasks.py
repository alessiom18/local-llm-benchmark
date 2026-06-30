#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Task del benchmark "Non esiste il modello migliore".
Ogni task ha controlli AUTOMATICI dove possibile (JSON valido, campi presenti, codice plausibile),
così il punteggio non dipende solo dal giudizio umano. I task sono richieste REALI di SmartShop
(gestionale negozi/ristoranti con AI locale) + generazione siti con scala di valutazione.
"""

# ---- helper di check (ritornano dict: {passed: bool, score: 0..1, note: str}) ----
import json, re

def _try_json(txt):
    txt = txt.strip()
    # togli eventuale fence ```json
    m = re.search(r'```(?:json)?\s*(.*?)```', txt, re.S)
    if m:
        txt = m.group(1).strip()
    # prendi dal primo { o [ all'ultimo } o ]
    s, e = re.search(r'[\{\[]', txt), None
    if s:
        txt = txt[s.start():]
    try:
        return json.loads(txt)
    except Exception:
        # ultimo tentativo: fino all'ultima graffa
        for end in (txt.rfind('}'), txt.rfind(']')):
            if end > 0:
                try:
                    return json.loads(txt[:end+1])
                except Exception:
                    pass
    return None

def chk_json_keys(keys):
    def f(txt):
        d = _try_json(txt)
        if d is None:
            return {'passed': False, 'score': 0.0, 'note': 'JSON non valido'}
        obj = d[0] if isinstance(d, list) and d else d
        if not isinstance(obj, dict):
            return {'passed': False, 'score': 0.3, 'note': 'JSON valido ma non un oggetto'}
        have = [k for k in keys if k in obj]
        sc = len(have) / len(keys)
        return {'passed': sc >= 0.6, 'score': round(sc, 2),
                'note': f'campi {len(have)}/{len(keys)}'}
    return f

def chk_json_list(min_items, item_keys):
    def f(txt):
        d = _try_json(txt)
        arr = None
        if isinstance(d, list):
            arr = d
        elif isinstance(d, dict):
            # qualunque chiave (items/piatti/menu/prodotti/...): prendi la prima lista di oggetti
            for v in d.values():
                if isinstance(v, list) and v and isinstance(v[0], dict):
                    arr = v; break
        if not isinstance(arr, list):
            return {'passed': False, 'score': 0.0, 'note': 'lista non trovata'}
        if not arr:
            return {'passed': False, 'score': 0.1, 'note': 'lista vuota'}
        good = sum(1 for it in arr if isinstance(it, dict) and all(k in it for k in item_keys))
        sc = min(1.0, len(arr) / min_items) * (good / len(arr))
        return {'passed': len(arr) >= min_items and good >= len(arr) * 0.7,
                'score': round(sc, 2), 'note': f'{len(arr)} elementi, {good} completi'}
    return f

def chk_code_flask(txt):
    has_route = '@app.route' in txt or 'app.route(' in txt
    has_def = bool(re.search(r'def\s+\w+\s*\(', txt))
    has_return = 'return' in txt
    sc = (has_route + has_def + has_return) / 3
    return {'passed': has_route and has_def, 'score': round(sc, 2),
            'note': f"route={has_route} def={has_def} return={has_return}"}

def chk_website(txt):
    t = txt.lower()
    has_html = '<html' in t or '<!doctype' in t
    has_head = '<style' in t or 'class=' in t
    n_sections = t.count('<section') + t.count('<div class')//3
    has_cta = ('href=' in t and ('ordina' in t or 'prenota' in t or 'contatt' in t or 'tel:' in t or 'wa.me' in t))
    closed = '</html>' in t
    length_ok = len(txt) > 1200
    score = sum([has_html, has_head, has_cta, closed, length_ok, n_sections >= 3]) / 6
    return {'passed': has_html and closed and length_ok, 'score': round(score, 2),
            'note': f"html={has_html} chiuso={closed} cta={has_cta} sez~{n_sections} len={len(txt)}"}

def chk_text_len(lo, hi):
    def f(txt):
        n = len(txt.split())
        ok = lo <= n <= hi
        # punteggio a campana morbida
        if n < lo:
            sc = n / lo
        elif n > hi:
            sc = max(0.3, hi / n)
        else:
            sc = 1.0
        return {'passed': ok, 'score': round(sc, 2), 'note': f'{n} parole (atteso {lo}-{hi})'}
    return f

def chk_nonempty(txt):
    n = len(txt.strip())
    return {'passed': n > 40, 'score': 1.0 if n > 40 else n/40, 'note': f'{n} caratteri'}


# ---- TASK ----
# category: classify | extract | config | strategy | recipe | code | copy | website
# expects: json|code|text|html  · np = num_predict
TASKS = [
    # --- CLASSIFICAZIONE INTENTO (JSON, verificabile) ---
    {'id': 'intent_tavolo', 'cat': 'classify', 'expects': 'json', 'np': 200,
     'sys': 'Sei il classificatore di un gestionale. Rispondi SOLO JSON.',
     'prompt': 'Classifica questa richiesta del negoziante in JSON {"intent":"...","oggetto":"...","azione":"..."}. Richiesta: «apri il tavolo 5 per 4 persone».',
     'check': chk_json_keys(['intent', 'oggetto', 'azione'])},
    {'id': 'intent_sconto', 'cat': 'classify', 'expects': 'json', 'np': 200,
     'sys': 'Sei il classificatore di un gestionale. Rispondi SOLO JSON.',
     'prompt': 'Classifica in JSON {"intent":"...","entita":"...","valore":"..."}. Richiesta: «metti il 20% di sconto su tutti i dolci».',
     'check': chk_json_keys(['intent', 'entita', 'valore'])},

    # --- ESTRAZIONE / STRUTTURAZIONE (JSON lista) ---
    {'id': 'menu_struttura', 'cat': 'extract', 'expects': 'json', 'np': 700,
     'sys': 'Strutturi dati per un menu digitale. Rispondi SOLO JSON.',
     'prompt': 'Trasforma questo testo in JSON lista di piatti [{"nome":...,"prezzo":...,"categoria":...}]: '
               '"Antipasti: bruschetta 5 euro, tagliere misto 12. Primi: carbonara 10, amatriciana 9,50. Dolci: tiramisù 5".',
     'check': chk_json_list(5, ['nome', 'prezzo'])},
    {'id': 'allergeni', 'cat': 'extract', 'expects': 'json', 'np': 300,
     'sys': 'Sei un esperto di sicurezza alimentare. Rispondi SOLO JSON.',
     'prompt': 'Elenca i probabili allergeni (dei 14 UE) di questo piatto in JSON {"allergeni":["..."]}. Piatto: "Lasagna alla bolognese con besciamella".',
     'check': chk_json_keys(['allergeni'])},

    # --- CONFIGURAZIONE (JSON) ---
    {'id': 'config_pizzeria', 'cat': 'config', 'expects': 'json', 'np': 400,
     'sys': 'Configuri un gestionale per tipo di attività. Rispondi SOLO JSON.',
     'prompt': 'Per una PIZZERIA da asporto proponi la config in JSON {"moduli":["..."],"reparti":["..."],"formula":"..."}.',
     'check': chk_json_keys(['moduli', 'reparti', 'formula'])},

    # --- STRATEGIA / CONSULENZA (testo, giudizio umano + lunghezza) ---
    {'id': 'strategia_martedi', 'cat': 'strategy', 'expects': 'text', 'np': 400,
     'sys': 'Sei un consulente commerciale per piccoli negozi italiani. Concreto, niente fuffa.',
     'prompt': 'Un ristorante è quasi vuoto il martedì sera. Dammi 3 idee CONCRETE e a basso costo per riempirlo, adatte a un locale di quartiere.',
     'check': chk_text_len(60, 350)},
    {'id': 'strategia_feature', 'cat': 'strategy', 'expects': 'text', 'np': 400,
     'sys': 'Sei lo stratega di prodotto di un gestionale AI locale per negozi.',
     'prompt': 'Suggerisci UNA funzione nuova, originale e utile per un gestionale di un parrucchiere. Spiega in breve perché venderebbe.',
     'check': chk_text_len(60, 350)},

    # --- RICETTA (testo strutturato) ---
    {'id': 'ricetta_vegana', 'cat': 'recipe', 'expects': 'text', 'np': 500,
     'sys': 'Sei uno chef. Ricette chiare con ingredienti e procedimento.',
     'prompt': 'Dammi una ricetta VEGANA e senza glutine per un primo piatto, con ingredienti (quantità) e procedimento in passi.',
     'check': chk_text_len(80, 400)},

    # --- CODICE (Flask, verificabile) ---
    {'id': 'code_endpoint', 'cat': 'code', 'expects': 'code', 'np': 500,
     'sys': 'Sei uno sviluppatore Flask. Codice essenziale e corretto.',
     'prompt': 'Scrivi una route Flask GET /api/incassi/settimana che somma i totali degli ultimi 7 giorni dalla tabella SQLite "transazioni" (colonne data, totale_cents) e ritorna JSON {"incasso_cents": N}. Usa get_db().',
     'check': chk_code_flask},
    {'id': 'code_review', 'cat': 'code', 'expects': 'text', 'np': 500,
     'sys': 'Sei un revisore di codice senior. Trova problemi reali.',
     'prompt': 'Rivedi questo codice e indica i problemi: \n'
               '```python\n@app.route("/api/sconto")\ndef sconto():\n    p = request.args.get("perc")\n    db.execute("UPDATE prodotti SET prezzo = prezzo - prezzo*"+p+"/100")\n    return "ok"\n```',
     'check': chk_nonempty},

    # --- COPYWRITING (testo) ---
    {'id': 'copy_prodotto', 'cat': 'copy', 'expects': 'text', 'np': 200,
     'sys': 'Scrivi testi brevi e invitanti per un menu.',
     'prompt': 'Scrivi una descrizione invitante (max 30 parole) per il piatto "Tagliata di manzo con rucola e grana".',
     'check': chk_text_len(8, 45)},

    # --- SITI WEB (HTML, scala di valutazione automatica) ---
    {'id': 'sito_pizzeria', 'cat': 'website', 'expects': 'html', 'np': 2200,
     'sys': 'Sei un web designer. Generi una pagina HTML completa, moderna, mobile-first, con CSS inline.',
     'prompt': 'Genera il sito vetrina (una pagina HTML completa, dal <!doctype> a </html>) per "Pizzeria Da Mario", Livorno, tel 0586 123456. '
               'Sezioni: hero, chi siamo, specialità, contatti. Includi un bottone «Ordina a domicilio». Colori caldi.',
     'check': chk_website},
    {'id': 'sito_parrucchiere', 'cat': 'website', 'expects': 'html', 'np': 2200,
     'sys': 'Sei un web designer. Generi una pagina HTML completa, moderna, mobile-first, con CSS inline.',
     'prompt': 'Genera il sito vetrina completo (HTML dal doctype a </html>) per il salone "Hair Studio Bella", Pisa, tel 050 987654. '
               'Sezioni: hero, servizi, listino, prenota. Includi un bottone «Prenota un appuntamento» (link WhatsApp). Stile elegante.',
     'check': chk_website},
]
