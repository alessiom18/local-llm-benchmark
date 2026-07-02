# Quale AI locale usare DAVVERO, per cosa
### La guida onesta: il modello giusto per ogni compito — e chi può prendere il posto di chi

*Di [SudoWAI](https://sudowai.com) — AI in locale, Livorno. Parte 7 della ricerca [«Non esiste il modello migliore»](../ARTICOLO.md). Frutto di oltre 2.000 test su 35 modelli, due computer.*

---

Dopo migliaia di prove, la domanda pratica è una sola: **quale modello uso, per cosa?** Non "il migliore in assoluto" (non esiste), ma il più adatto a ogni lavoro, su hardware normale (una scheda video da poche centinaia di euro). Ecco la nostra guida — basata sui dati, non sul marketing.

## La tabella: compito → modello giusto
| Ti serve per… | Usa | Perché |
|---|---|---|
| **Configurare, testi, strategia** | **Gemma 12B** | Il nostro tuttofare: qualità alta, affidabile sui compiti reali del gestionale |
| **Leggere foto → prodotti/menu** | **Gemma 12B (vision)** | Legge menu e scaffali; gli altri "vedono" cose che non ci sono (allucinano) |
| **Scrivere codice** | **Gemma 12B** | Nei nostri A/B batte i modelli "da codice" e resta in memoria con gli altri servizi |
| **Risposte rapide, volumi** | **Cogito 8B** | ~3× più veloce, passa i controlli: perfetto quando conta la reattività |
| **Ragionare, prevedere, strategia complessa** | **DeepSeek-R1 / Phi-4** | Guardano "avanti": piani a fasi con conseguenze e contromosse |
| **Il massimo su compito difficile** | **Phi-4 14B** | Nel bench esteso batte modelli quasi doppi |

## Il colpo di scena: chi prende il posto di chi
- **Gemma 12B prende il posto della 31B**: stessa qualità, **~13× più veloce**. La versione grande, sul nostro hardware, non vale il costo.
- **Phi-4 14B batte i 24–26B**: la taglia non fa la qualità.
- **Un modello fuso da 7B ha battuto il suo "genitore"** (0,71 vs 0,64): fondere bene *migliora*, restando piccolo.
- **Il "thinking" (ragionamento verboso) va spento** sui compiti concreti: un modello è crollato dall'80% allo 0% di risposte corrette con il ragionamento acceso. Tienilo solo per lo stratega.

## E rispetto al cloud a pagamento?
Onestà prima di tutto: un modello locale distillato **non è più intelligente** di un grande servizio cloud — spesso è una sua *copia compressa*. Il vantaggio **non è intellettuale, è pratico**, ed è enorme per un'azienda:
- **Gira in casa**: i dati non escono, zero costi d'uso, funziona offline
- **Non te lo possono togliere** (nessun decreto, nessun abbonamento che raddoppia)
- **È tuo**: lo modifichi, lo specializzi sulla tua attività

Per la maggior parte dei compiti di un negozio o di un ristorante — configurare il menu, leggere una foto, scrivere una descrizione, suggerire una promozione — **un Gemma 12B in locale fa il lavoro**, con i dati che restano a casa tua. Il "cervellone cloud" serve molto meno di quanto ti raccontino.

## La regola d'oro
Non chiedere *"qual è il modello più potente?"*. Chiedi *"qual è il modello giusto per QUESTO compito, che posso controllare?"*. È esattamente ciò che fa **SmartShop**: sotto il cofano non c'è "il modello di moda", c'è un **sistema** che sceglie lo strumento adatto, in locale, per ogni lavoro.

*Dati e codice: [github.com/alessiom18/local-llm-benchmark](https://github.com/alessiom18/local-llm-benchmark) · [sudowai.com/ricerca-ai](https://sudowai.com/ricerca-ai) · SudoWAI, Livorno.*
