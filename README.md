# local-llm-benchmark

**Non esiste "il modello migliore".** Banco di prova per modelli LLM **in locale** (Ollama), provati sui compiti
reali di un gestionale ([SmartShop](https://smartshop.sudowai.com) di [SudoWAI](https://sudowai.com)):
classificare richieste, estrarre menù, scrivere/rivedere codice, generare siti, dare consigli.

👉 **Articolo completo e risultati:** [ARTICOLO.md](ARTICOLO.md)
\n🌐 **Leggi la ricerca sul nostro sito:** [sudowai.com/ricerca-ai](https://sudowai.com/ricerca-ai)


## La ricerca in 3 parti
1. [Non esiste il modello migliore](ARTICOLO.md) — la classifica (decine di modelli, piccolo batte grande)
2. [I benchmark mentono](docs/02-i-benchmark-mentono.md) — il metodo (perché i test ingenui ingannano)
3. [Fondere i modelli + la flotta](docs/03-fusione-e-flotta.md) — gli esperimenti (fusione onesta, due PC che collaborano)
4. [Anche le AI credono che grande=meglio](docs/04-i-bias-delle-ai.md) — i bias (autolavaggio + la squadra)

## Perché
Le classifiche online sono fatte su benchmark accademici lontani dal lavoro vero, e spesso premiano la *forma*
non la *sostanza*. Qui i compiti sono reali e la qualità è valutata da un **giudice LLM cieco** (con riprova del
modello vincente + verifica umana a campione), non solo da check automatici.

## Hardware di riferimento
RTX 3060 12GB + 31GB RAM — hardware "da retrobottega", niente cloud.

## Come riprodurlo
```bash
# 1) esegui i modelli sui compiti (deadline-aware, salva incrementale)
python3 run_bench.py --until 06:45

# 2) rigenera i compiti "aperti" con spazio token abbondante (no troncamenti)
python3 run_open_clean.py

# 3) varianti: thinking ON/OFF + stile "caveman"
python3 run_variants.py

# 4) giudizio di qualità (giudice cieco, voto 1-5 sui compiti aperti)
python3 judge.py results/results_merged_XXXX.jsonl --judge gemma4:31b

# 5) tabelle + grafici
python3 analyze.py

# pagina live durante i test
python3 live_server.py 8899   # → http://localhost:8899
```

## File
- `tasks.py` — i 13 compiti + i controlli automatici (correttezza di forma)
- `run_bench.py` — esecuzione modello × compito, misure (tempo, token, tok/s)
- `run_open_clean.py` — rerun dei compiti aperti con token abbondanti (no troncamento)
- `run_variants.py` — thinking on/off + caveman
- `judge.py` — giudice LLM cieco (qualità 1-5) sui compiti aperti
- `analyze.py` — classifiche + grafici (`report/`)
- `live_server.py` — dashboard live
- `results/` — dati grezzi di ogni run (trasparenza totale)

## Metodologia in breve
- **Compiti oggettivi** (JSON/codice): check automatico = cancello di correttezza.
- **Compiti aperti** (consigli/ricette/siti): **giudice LLM cieco**, rubrica per categoria, voto 1-5 → 0-1.
- **Niente penalità per troncamento**: le risposte tagliate dal limite token vengono rigenerate con spazio.
- **Riprova**: il modello risultato migliore rifà da giudice; campione di giudizi verificato a mano.

## Licenza
MIT. *SudoWAI — Livorno. AI in locale, senza Big Tech.*
