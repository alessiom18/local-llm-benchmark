# Benchmark Real-World: 40 Modelli LLM Locali a Confronto

**Data:** 27 Luglio 2026  
**Hardware:** RTX 3060 12GB + 31GB RAM  
**Metodo:** 10 task reali × 40 modelli Ollama = 400 test  
**Giudice:** Check automatici (no giudizio umano)  
**Repository:** [local-llm-benchmark](https://github.com/alessiom18/local-llm-benchmark)

> "Non esiste il modello migliore" — ma esiste il modello migliore PER OGNI COMPITO.

## Domande del test

| # | Task | Tipo | Cosa testa |
|---|------|------|-----------|
| 1 | `inv_find_bug` | Indagine | Analizza codice Flask, trova bug di sicurezza e logica |
| 2 | `diag_ev_system` | Diagnosi | Diagnostiche veicolo EV con sintomi multipli |
| 3 | `create_dispensa` | Creazione | Genera dispensa tecnica pratica completa |
| 4 | `search_mosfet` | Ricerca | Confronta componenti elettronici con pro/contro |
| 5 | `fix_injection` | Fix | Correggi SQL injection mantenendo funzionalità |
| 6 | `predict_batt_degrad` | Predizione | Prevedi degradamento batteria e proponi mitigazioni |
| 7 | `multi_build_scooter` | Multi-fase | Piano completo conversione elettrica con budget |
| 8 | `code_battery_monitor` | Coding | Script Python reale con ADC, CSV, gestione errori |
| 9 | `search_tools` | Ricerca | 5 strumenti indispensabili per officina EV |
| 10 | `diag_comm_error` | Diagnosi | Debug errore comunicazione display-sensore |

---

## Classifica Generale

Ordinata per score medio (0-1), tempo medio, e completezza.

| # | Modello | Score | Min | Max | StdDev | Tempo | tok/s | OK | Tier |
|---|---------|-------|-----|-----|--------|-------|-------|----|------|
| 1 | **qwen3.5:latest** | **0.900** | 0.67 | 1.00 | 0.11 | 19s | 68.4 | 10/10 | light |
| 2 | **qwen2.5-coder:14b** | **0.892** | 0.67 | 1.00 | 0.12 | 33s | 52.2 | 10/10 | light |
| 3 | **command-r7b** | **0.875** | 0.67 | 1.00 | 0.14 | 13s | 78.5 | 10/10 | light |
| 4 | **gemma4:12b** | **0.875** | 0.67 | 1.00 | 0.13 | 23s | 31.1 | 10/10 | light |
| 5 | **gemma4:26b** | **0.867** | 0.67 | 1.00 | 0.13 | 30s | 33.8 | 10/10 | heavy |
| 6 | **gemma:7b** | **0.859** | 0.67 | 1.00 | 0.13 | 8s | 89.4 | 10/10 | light |
| 7 | gemma4:latest | 0.842 | 0.67 | 1.00 | 0.13 | 13s | 32.6 | 10/10 | light |
| 8 | wizardlm2:7b | 0.834 | 0.67 | 1.00 | 0.13 | 11s | 34.6 | 10/10 | light |
| 9 | deepseek-coder-v2:16b | 0.817 | 0.67 | 1.00 | 0.14 | 12s | 29.1 | 10/10 | light |
| 10 | qwen2.5:7b | 0.817 | 0.67 | 1.00 | 0.13 | 12s | 35.5 | 10/10 | light |
| 11 | deepseek-r1:8b | 0.817 | 0.67 | 1.00 | 0.13 | 14s | 26.6 | 10/10 | light |
| 12 | qwen3.6:35b | 0.808 | 0.67 | 1.00 | 0.14 | 29s | 23.7 | 10/10 | heavy |
| 13 | qwen2.5:3b | 0.800 | 0.67 | 1.00 | 0.14 | 31s | 38.2 | 10/10 | light |
| 14 | qwen2.5:14b | 0.800 | 0.67 | 1.00 | 0.13 | 34s | 32.9 | 10/10 | light |
| 15 | qwen-fuso:7b | 0.792 | 0.67 | 1.00 | 0.14 | 13s | 36.4 | 10/10 | light |
| 16 | nemotron-cascade-2:30b | 0.792 | 0.50 | 1.00 | 0.16 | 33s | 15.9 | 10/10 | heavy |
| 17 | serena-v6:latest | 0.792 | 0.67 | 1.00 | 0.13 | 10s | 32.1 | 10/10 | light |
| 18 | phi4-mini:latest | 0.792 | 0.50 | 1.00 | 0.16 | 7s | 52.1 | 10/10 | light |
| 19 | deepseek-r1:14b | 0.792 | 0.50 | 1.00 | 0.15 | 34s | 20.8 | 10/10 | light |
| 20 | dolphin-llama3:8b | 0.784 | 0.67 | 1.00 | 0.13 | 9s | 38.7 | 10/10 | light |
| 21 | qwen2.5:14b-instruct | 0.784 | 0.67 | 1.00 | 0.14 | 33s | 33.2 | 10/10 | light |
| 22 | hermes3:8b | 0.775 | 0.67 | 1.00 | 0.14 | 10s | 36.9 | 10/10 | light |
| 23 | mistral-nemo:latest | 0.775 | 0.50 | 1.00 | 0.17 | 16s | 22.1 | 10/10 | light |
| 24 | gemma4:e4b | 0.767 | 0.67 | 1.00 | 0.14 | 14s | 25.2 | 10/10 | light |
| 25 | gemma3:4b | 0.759 | 0.67 | 1.00 | 0.14 | 9s | 29.5 | 10/10 | light |
| 26 | dolphin3:8b | 0.758 | 0.50 | 1.00 | 0.16 | 12s | 32.1 | 10/10 | light |
| 27 | devstral:24b | 0.742 | 0.50 | 1.00 | 0.16 | 123s | 6.2 | 10/10 | heavy |
| 28 | codestral:22b | 0.734 | 0.67 | 1.00 | 0.13 | 96s | 5.8 | 10/10 | heavy |
| 29 | cogito:8b | 0.725 | 0.50 | 1.00 | 0.16 | 11s | 35.4 | 10/10 | light |
| 30 | qwen2.5-coder:7b | 0.717 | 0.50 | 1.00 | 0.17 | 12s | 34.1 | 10/10 | light |
| 31 | Qwen2.5-Coder-32B abliterated | 0.717 | 0.50 | 1.00 | 0.17 | 197s | 5.1 | 9/10 | heavy |
| 32 | phi4:latest | 0.709 | 0.50 | 1.00 | 0.16 | 42s | 16.3 | 10/10 | light |
| 33 | nous-hermes2:latest | 0.705 | 0.50 | 1.00 | 0.18 | 11s | 35.2 | 10/10 | light |
| 34 | qwen2.5:0.5b | 0.683 | 0.33 | 1.00 | 0.20 | 2s | 56.8 | 10/10 | light |
| 35 | gemma:2b | 0.625 | 0.25 | 1.00 | 0.24 | 7s | 18.9 | 10/10 | light |
| 36 | qwen3:4b | 0.416 | 0.00 | 1.00 | 0.32 | 9s | 22.4 | 10/10 | light |
| 37 | starcoder2:15b | 0.387 | 0.00 | 1.00 | 0.35 | 8s | 31.1 | 10/10 | light |
| 38 | gemma4:31b | 0.342 | 0.00 | 1.00 | 0.38 | 122s | 3.9 | 5/10 | heavy |
| 39 | gpt-oss:20b | 0.200 | 0.00 | 0.75 | 0.22 | 27s | 14.2 | 10/10 | heavy |
| 40 | llama3:text | 0.086 | 0.00 | 0.25 | 0.09 | 4s | 22.3 | 10/10 | light |

---

## Analisi per Categoria

### 🔍 Indagine Codice (inv_find_bug)
Test: analizza codice Flask e trova bug di sicurezza e logica.

| # | Modello | Score | Tempo |
|---|---------|-------|-------|
| 1 | qwen2.5-coder:14b | 1.000 | 50s |
| 2 | wizardlm2:7b | 1.000 | 13s |
| 3 | command-r7b | 1.000 | 25s |
| 4 | qwen3.6:35b | 1.000 | 85s |
| 5 | qwen3.5:latest | 1.000 | 35s |

### 🩺 Diagnosi Tecnica (diag_ev_system + diag_comm_error)
Test: diagnosticare veicoli EV con sintomi complessi.

| # | Modello | Score | Tempo |
|---|---------|-------|-------|
| 1 | qwen2.5-coder:14b | 1.000 | 29s |
| 2 | nous-hermes2 | 1.000 | 12s |
| 3 | command-r7b | 1.000 | 11s |
| 4 | cogito:8b | 1.000 | 10s |
| 5 | gemma4:latest | 1.000 | 9s |

### 📝 Creazione Contenuto (create_dispensa + code_battery_monitor)
Test: generare documentazione tecnica e codice funzionante.

| # | Modello | Score | Tempo |
|---|---------|-------|-------|
| 1 | codestral:22b | 1.000 | 106s |
| 2 | deepseek-coder-v2:16b | 1.000 | 12s |
| 3 | qwen2.5-coder:14b | 1.000 | 42s |
| 4 | qwen2.5-coder:7b | 1.000 | 11s |
| 5 | wizardlm2:7b | 1.000 | 13s |

### 🔬 Ricerca Tecnica (search_mosfet + search_tools)
Test: cercare, confrontare, raccomandare componenti.

| # | Modello | Score | Tempo |
|---|---------|-------|-------|
| 1 | gemma:7b | 0.750 | 8s |
| 2 | deepseek-coder-v2:16b | 0.625 | 9s |
| 3 | qwen2.5-coder:14b | 0.625 | 29s |
| 4 | wizardlm2:7b | 0.625 | 8s |
| 5 | hermes3:8b | 0.625 | 9s |

### 🔒 Fix Sicurezza (fix_injection)
Test: correggere SQL injection mantenendo la funzionalità.

| # | Modello | Score | Tempo |
|---|---------|-------|-------|
| 1 | deepseek-coder-v2:16b | 1.000 | 9s |
| 2 | starcoder2:15b | 1.000 | 24s |
| 3 | qwen2.5-coder:14b | 1.000 | 29s |
| 4 | qwen2.5-coder:7b | 1.000 | 10s |
| 5 | qwen2.5:0.5b | 1.000 | 2s |

### 🔮 Predizione Problemi (predict_batt_degrad)
Test: anticipare problemi futuri e proporre mitigazioni.

| # | Modello | Score | Tempo |
|---|---------|-------|-------|
| 1 | command-r7b | 1.000 | 11s |
| 2 | hermes3:8b | 1.000 | 9s |
| 3 | qwen-fuso:7b | 1.000 | 10s |
| 4 | Qwen2.5-Coder-32B | 1.000 | 203s |
| 5 | nemotron-cascade-2 | 1.000 | 33s |

### 📋 Compito Multi-Fase (multi_build_scooter)
Test: piano completo con più fasi, budget, tempistiche.

| # | Modello | Score | Tempo |
|---|---------|-------|-------|
| 1 | codestral:22b | 1.000 | 96s |
| 2 | deepseek-coder-v2:16b | 1.000 | 19s |
| 3 | qwen2.5-coder:14b | 1.000 | 26s |
| 4 | qwen2.5-coder:7b | 1.000 | 12s |
| 5 | nous-hermes2 | 1.000 | 12s |

---

## I Più Sorprendenti

### 🏆 Chi batte modelli più grandi

| Piccolo | Score | Grande superato | Score |
|---------|-------|-----------------|-------|
| gemma:7b (0.859) | #6 | gemma4:31b (0.342) | #38 |
| qwen2.5:3b (0.800) | #13 | Qwen2.5-Coder-32B (0.717) | #31 |
| phi4-mini (0.792) | #18 | phi4 (0.709) | #32 |
| command-r7b (0.875) | #3 | devstral:24b (0.742) | #27 |

### 📉 I Deludenti

| Modello | Score | Problema |
|---------|-------|----------|
| gemma4:31b | 0.342 | Troppo grande per 3060, 5/10 task falliti |
| gpt-oss:20b | 0.200 | Non riesce a completare task complessi |
| llama3:text | 0.086 | Modello text-only, inadatto a questi task |
| qwen3:4b | 0.416 | Nuovo ma peggio dei predecessori |
| starcoder2:15b | 0.387 | Specializzato coding, male su tutto il resto |

### ⚡ I Più Velocei con Score Alto

| Modello | Score | Tempo | Ratio score/tempo |
|---------|-------|-------|-------------------|
| gemma:7b | 0.859 | 8s | 0.107 |
| command-r7b | 0.875 | 13s | 0.067 |
| phi4-mini | 0.792 | 7s | 0.113 |
| wizardlm2:7b | 0.834 | 11s | 0.076 |
| qwen3.5:latest | 0.900 | 19s | 0.047 |

---

## Raccomandazioni per OpenCode

### Per sviluppo + ricerca + indagine

| Uso | Modello consigliato | Score | Tempo |
|-----|-------------------|-------|-------|
| **Miglior overall** | qwen3.5:latest | 0.900 | 19s |
| **Miglior coding** | qwen2.5-coder:14b | 0.892 | 33s |
| **Miglior velocità** | gemma:7b | 0.859 | 8s |
| **Bilanciato** | gemma4:12b | 0.875 | 23s |
| **Best rapporto qualità/velocità** | command-r7b | 0.875 | 13s |

### Per Jarvis Team (agenti multipli)

| Ruolo | Modello | Perché |
|-------|---------|--------|
| **Esploratore** | gemma:7b | Veloce, buon score, analizza codice |
| **Operatore** | qwen2.5-coder:14b | Miglior coding + diagnosi |
| **Revisore** | qwen3.5:latest | Score più alto, verifica qualità |

---

## Metodologia

### Hardware
- **GPU:** NVIDIA RTX 3060 12GB
- **RAM:** 31GB DDR4
- **OS:** Linux
- **Runner:** Ollama (localhost:11434)

### Parametri
- **Temperature:** 0.2 (JSON), 0.5 (testo)
- **Think:** Off (per tutti)
- **Timeout:** 300s per task
- **Num_predict:** ridotto per modelli heavy su task website

### Check Automatici
- **JSON:** validità + chiavi presenti
- **Codice:** presenza di def, return, import
- **Testo:** lunghezza minima + struttura
- **Diagnosi:** problema + causa + soluzione + test
- **Ricerca:** fonti + confronto + consiglio
- **Predizione:** scenario + rischio + mitigazione
- **Multi-step:** passi strutturati + dettaglio

### Limitazioni
- Check automatici non valutano la qualità semantica
- Nessun giudice LLM cieco (come nel benchmark originale)
- Task specifici per dominio EV/gestionale
- Hardware limitato (modelli >25B soffrono)

---

## Dati Grezzi

- **Risultati:** `results/results_realworld_20260727_1255.jsonl`
- **Analisi:** `results/analysis_realworld.json`
- **Classifica:** `results/classifica_realworld_20260727_1255.json`
- **Log:** `results/bench_realworld_full.log`

---

*SudoWAI — Livorno. AI in locale, senza Big Tech.*
