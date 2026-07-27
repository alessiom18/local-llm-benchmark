#!/usr/bin/env python3
"""Task definitions per il benchmark real-world."""

CODE_WITH_BUG = '''@app.route("/api/bilancia", methods=["POST"])
def bilancia():
    data = request.json
    cella = data["cella"]
    target = data["target_voltage"]
    db.execute("UPDATE celle SET voltage = ? WHERE id = ?", (target, cella))
    return jsonify({"ok": True})'''

REAL_TASKS = [
    {'id': 'inv_find_bug', 'cat': 'investigate', 'expects': 'text', 'np': 600,
     'sys': 'Sei un senior developer. Analizzi codice e trovi problemi di sicurezza e logica.',
     'prompt': f'Analizza questo codice Flask e trova TUTTI i problemi (sicurezza, logica, errori). Spiegali in ordine di gravità:\n```python\n{CODE_WITH_BUG}\n```'},

    {'id': 'diag_ev_system', 'cat': 'diagnose', 'expects': 'text', 'np': 600,
     'sys': 'Sei un tecnico EV esperto. Diagnostiche sistematiche e precise.',
     'prompt': 'Un veicolo elettrico 48V ha questi sintomi: parte, va per 5 minuti, poi si ferma. Display mostra "E-03". Dopo 10 minuti riparte. Riparte dopo 5 minuti. Fai una diagnosi completa: possibili cause, test da fare, soluzione.'},

    {'id': 'create_dispensa', 'cat': 'create', 'expects': 'text', 'np': 1200,
     'sys': 'Sei un formatore EV. Scrivi dispense pratiche, italiane, da officina.',
     'prompt': 'Scrivi una dispensa pratica (massimo 2 pagine) su "Come diagnosticare un BMS guasto". Deve avere: cosa serve, come si misura, errori comuni, quando chiedere aiuto. Italiano semplice, elenchi puntati, emoji per i punti chiave.'},

    {'id': 'search_mosfet', 'cat': 'search', 'expects': 'text', 'np': 600,
     'sys': 'Sei un esperto di componenti elettronici.',
     'prompt': 'Confronta MOSFET per controller EV: IRF3205 vs IRF1404 vs IRFZ44N. Per ogni uno: specifiche, prezzo indicativo, dove si trova, pro/contro. Quale scegliere per un motorino 48V 1000W e perché.'},

    {'id': 'fix_injection', 'cat': 'fix', 'expects': 'text', 'np': 600,
     'sys': 'Sei un sicurezzista. Correggi vulnerabilità senza rompere la funzionalità.',
     'prompt': f'Correggi questo codice eliminando la SQL injection. Spiega ogni modifica:\n```python\n{CODE_WITH_BUG}\n```'},

    {'id': 'predict_batt_degrad', 'cat': 'predict', 'expects': 'text', 'np': 600,
     'sys': 'Sei un esperto di batterie EV.',
     'prompt': 'Un utente ha una bici elettrica 48V 20Ah con 300 cicli. Vive a Livorno (clima mite). Va al lavoro 10km al giorno. Prevedi i problemi che avrà nei prossimi 6 mesi e come prevenirli.'},

    {'id': 'multi_build_scooter', 'cat': 'multi_step', 'expects': 'text', 'np': 1200,
     'sys': 'Sei un EV builder esperto.',
     'prompt': 'Voglio convertire un Piaggio Ciao 50 in elettrico. Budget 800€. Voglio almeno 40km di autonomia e 45km/h. Fai un piano completo: componenti (con prezzi), fasi di lavoro, tempistiche, rischi, cosa posso fare da solo e cosa delegare.'},

    {'id': 'code_battery_monitor', 'cat': 'create', 'expects': 'code', 'np': 800,
     'sys': 'Sei uno sviluppatore Python embedded.',
     'prompt': 'Scrivi uno script Python che: 1) Legge la tensione di una cella Li-ion via ADC ADS1115 2) Calcola lo stato di carica (SOC) con curva approssimativa 3) Accende un LED verde se >50%, giallo se 20-50%, rosso se <20% 4) Logga tutto su file CSV con timestamp. Include gestione errori.'},

    {'id': 'search_tools', 'cat': 'search', 'expects': 'text', 'np': 600,
     'sys': 'Sei un esperto di strumenti da officina EV.',
     'prompt': 'Quali sono i 5 strumenti INDISPENSABILI per un officina EV? Per ognuno: marca/modello consigliato, prezzo, dove comprarlo in Italia, perché è fondamentale. Ordine per importanza.'},

    {'id': 'diag_comm_error', 'cat': 'diagnose', 'expects': 'text', 'np': 600,
     'sys': 'Sei un tecnico diagnostico EV.',
     'prompt': 'Un display EV mostra dati di velocità erratici (va da 0 a 999 km/h random). La velocità reale è costante a 25km/h. Il sensore Hall è nuovo. I cavi sono stati sostituiti di recente. Diagnostica il problema passo per passo.'},
]
