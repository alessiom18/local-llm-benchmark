# Non esiste "il modello migliore"
### 9 modelli di AI in locale, su hardware da retrobottega, sui compiti veri di un gestionale

*Di [SudoWAI](https://sudowai.com) — software e AI in locale, senza Big Tech · Livorno.*

---

## In due righe
Abbiamo messo alla prova **9 modelli di intelligenza artificiale interamente in locale** (nessun cloud) sui compiti reali del nostro gestionale **SmartShop**. Conclusione netta e contro-intuitiva: **non vince sempre lo stesso modello, e il più grosso non è il migliore.** Un modello "piccolo" da 12 miliardi di parametri ha **eguagliato uno quasi tre volte più grande, andando ~13× più veloce** — battendo perfino un modello da 70 miliardi.

## Hardware
**RTX 3060 12GB + 31GB di RAM.** Niente di esotico: il tipo di macchina che può stare nel retro di un negozio. Tutto in locale, dati che non escono di casa.

## I 9 modelli
Qwen2.5 3B · Cogito 8B · **Gemma4 12B** · Qwen2.5-Coder 14B · DeepSeek-Coder-V2 16B · Gemma4 31B · Qwen3.6 35B (MoE) · Qwen2.5-Coder 32B *abliterated* · Llama-3.3 70B *abliterated*.

## I compiti (13, reali)
Classificare richieste in linguaggio naturale, estrarre un menù in dati strutturati, riconoscere allergeni, configurare il gestionale, dare consigli commerciali, scrivere ricette, scrivere e **rivedere** codice, copywriting, **generare siti web**. Tutto ciò che SmartShop chiede all'AI ogni giorno.

---

## Prima lezione (a nostre spese): i benchmark ingenui MENTONO
Il primo giro ha dato una classifica **assurda**: un modello da 3 miliardi primo, uno da 31 ultimo. Il motivo è la trappola in cui cascano tanti benchmark fai-da-te: **misuravano la forma, non la sostanza** (è un JSON valido? c'è la funzione? la lunghezza è giusta?) — cose che anche un modello piccolo fa benissimo. Così tutti prendevano il massimo, e i modelli migliori venivano perfino **penalizzati** perché scrivevano risposte più ricche che un controllo ingenuo tagliava.

Due correzioni hanno cambiato tutto:
1. **Niente penalità per il limite tecnico.** Decine di risposte erano solo *troncate* per poco spazio: le abbiamo rifatte con spazio abbondante.
2. **Un giudice vero, anzi tre.** Per i compiti aperti un controllo automatico non basta: un **modello giudice valuta alla cieca** (voto 1–5, rubrica). Come riprova **il modello risultato migliore ha rifatto da giudice**, e una **valutazione esterna indipendente** ha controllato un campione. *Se un benchmark dà a tutti 10, il benchmark è rotto.*

---

## Risultati (classifica giudicata)

![Classifica giudicata](report/chart_judged.png)

| # | Modello | Qualità (0–1) |
|---|---------|---------------|
| 1 | **Gemma4 12B** | **0.77** |
| 1 | Gemma4 31B | 0.77 |
| 3 | Llama-3.3 70B abliterated | 0.73 |
| 4 | Qwen3.6 35B (MoE) | 0.69 |
| 4 | Qwen2.5-Coder 32B abliterated | 0.69 |
| 6 | Cogito 8B | 0.65 |
| 7 | Qwen2.5-Coder 14B | 0.62 |
| 8 | Qwen2.5 3B | 0.54 |
| 9 | DeepSeek-Coder-V2 16B | 0.47 |

**Il dato che conta:** **Gemma4 12B pareggia Gemma4 31B** (modello ~3× più grande) **e supera il Llama 70B.**

### E la velocità? Qui il quadro si ribalta
![Velocità](report/chart_speed.png)

- Gemma4 **12B: ~33 token/s**
- Gemma4 **31B: ~2,6 token/s**
- Llama **70B: ~1,3 token/s**

Stessa qualità del 31B, **~13 volte più veloce**. I giganti, a parità (o meno) di qualità, sono **inutilizzabili** per il lavoro reale su questo hardware.

![Quadrante qualità × velocità](report/chart_quadrant.png)

In alto a destra — bravi **e** veloci — ci finiscono i modelli **contenuti**, non i colossi.

### Chi vince su cosa
Modelli diversi vincono compiti diversi: i tre giudici concordano sul **cluster di testa** (modelli piccoli/medi) e sui **fanalini** (Qwen 3B, DeepSeek-Coder), e divergono solo sul "primo assoluto". Anche **scegliere il giudice è una scelta che pesa** → motivo in più per non fidarsi di una classifica unica. Dettaglio: [giudizio esterno](report/giudizio_claude.md).

---

## Thinking sì o no?
Abbiamo provato il "ragionamento esplicito" (*thinking*) acceso vs spento. Risultato chiaro: **quasi sempre peggiora** sui compiti strutturati.

![Thinking ON vs OFF](report/chart_thinking.png)

- Cogito 8B: 100% → 70%
- Gemma4 31B: 80% → 50%
- **Qwen3.6 35B: 80% → 0%** (col thinking **rompe il formato JSON**)

Sui compiti concreti (configurazioni, dati, codice) il thinking **va tenuto spento**. Serve, semmai, solo sui compiti aperti/strategici.

---

## La tesi: non un cervello gigante, ma un buon direttore d'orchestra
> **Il valore non è nel modello più grande. È nel SISTEMA che manda il modello giusto a fare la cosa giusta.**

Un modello piccolo e veloce per capire e smistare; uno per il codice; uno per la visione (foto → prodotti); uno "stratega" solo quando serve. Un setup **contenuto** rende più di un singolo gigante generico — a una frazione di energia, **in locale**, senza mandare i dati di nessuno nel cloud. È esattamente il motore di **MARCO** (orchestrazione + routing + *merge* + quantizzazione dinamica) dietro **SmartShop**.

E lo conferma il mercato: persino **OpenAI ha chiuso Sora** perché la generazione video di frontiera costava **~1 milione di dollari al giorno**. La potenza bruta nel cloud non regge. La via sostenibile è l'efficienza.

---

## Aggiornamento — la ricerca si allarga (più modelli, più macchine)
Per non fermarci a un solo computer, abbiamo esteso le prove a **più famiglie di modelli** e le abbiamo fatte girare anche su un **secondo nodo locale più potente** (una scheda video di fascia superiore), collegato in modo sicuro alla nostra rete — un primo esempio concreto di **"flotta": più macchine che collaborano** invece di un unico server.

Modelli/famiglie aggiunti e misurati (velocità reale sul secondo nodo):

| Modello (famiglia) | Velocità |
|---|---|
| Llama 3.1 8B | ~52 tok/s |
| Gemma 2 9B | ~23 tok/s |
| Gemma4 26B | ~23 tok/s |
| Mistral-Nemo 12B | ~16 tok/s |
| Nemotron 24B | ~12 tok/s |
| DeepSeek-R1 14B · Phi-4 14B | ~8 tok/s |

Questo copre le principali "scuole" di modelli aperti (Meta, Google, Mistral, Microsoft, Nvidia, DeepSeek, Alibaba/Qwen). E la **classifica di qualità estesa** (giudicata alla cieca) conferma tutto:

| # | Modello | Qualità (0–1) |
|---|---------|---------------|
| 1 | **Phi-4 14B** (Microsoft) | **0.79** |
| 2 | Nemotron 24B (Nvidia) | 0.75 |
| 3 | Qwen 14B *abliterated* | 0.73 |
| 4 | Gemma 26B · Qwen-Coder 14B · Gemma 2 9B · Mistral-Nemo 12B | 0.69 |
| 8 | DeepSeek-R1 14B | 0.65 |
| 9 | Llama 3.1 8B | 0.50 |

**Il dato che chiude il discorso:** vince un **14B (Phi-4)**, davanti ai 24-26B. Sommato al primo test (dove un 12B pareggiava un 31B), la conclusione regge ormai su **una dozzina di modelli e sette famiglie diverse**: *la taglia non fa la qualità.*

## Esperimento — fondere i modelli ("dare nuove abilità")
Abbiamo anche provato a **fondere** più modelli specializzati in uno solo (SLERP, TIES, DARE, frankenmerge) — l'equivalente di dare a un modello le abilità di più esperti. Risultato onesto: **su questo primo tentativo la fusione è degenerata** (i modelli fusi producevano testo incomprensibile, mentre i "genitori" funzionavano bene). Una lezione importante, spesso taciuta: **fondere i modelli non è magia gratis** — serve la ricetta giusta e strumenti stabili, altrimenti si rompe ciò che funzionava. È un lavoro in corso: lo rifaremo con un metodo più solido e lo racconteremo coi numeri, buoni o cattivi che siano. *(È anche il senso della ricerca aperta: pubblichiamo pure ciò che non ha funzionato.)*

---

## Riproducibilità
Tutto il codice è in questo repository: i 13 compiti (`tasks.py`), il runner (`run_bench.py`), la rigenerazione senza troncamenti (`run_open_clean.py`), le varianti thinking/caveman (`run_variants.py`), il giudice cieco (`judge.py`), i grafici (`make_charts.py`) e **tutti i dati grezzi** (`results/`). Chiunque può rifare i test sul proprio hardware.

*SudoWAI — Livorno. SmartShop (gestionale con AI locale), Serena (assistente WhatsApp), M.A.R.C.O. — self-hosted, niente Big Tech.*
