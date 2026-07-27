# Sei AI, una sola risposta: il consenso come bias

**Esperimento** — Stessa domanda ("voglio costruire un mio modello locale specializzato
su gestionale + diagnostica e-bike; valuta fine-tuning / distillazione / RAG / merging;
sii brutalmente onesto") posta a **6 modelli di frontiera**: ChatGPT, Copilot, Grok,
DeepSeek, Gemini, Claude. Più tre controlli locali: **uncensored** (dolphin), **abliterated**
(Qwen-32B) e **base/pre-instruct** (llama3:text).

Obiettivo: non "chi ha ragione", ma **quanto le AI pensano tutte uguale**, da dove viene, e cosa
resta quando togli censura, allineamento o entrambi.

---

## 1. Il consenso (impressionante)

Tutti e 6, indipendentemente, hanno dato la STESSA risposta strutturale:

| Tesi | ChatGPT | Copilot | Grok | DeepSeek | Gemini | Claude |
|---|:-:|:-:|:-:|:-:|:-:|:-:|
| "Non è fine-tuning, è architettura" | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| RAG/GraphRAG + Tool-calling = cuore | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Fine-tuning solo per *stile*, non conoscenza | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **27B in training = morto sul 3060** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Swap NON sblocca il training** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Merging/MoE = fragile, evita | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Distillazione = rischiosa senza revisione | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Servono 200–500 esempi "gold" curati a mano | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Unsloth + Qwen/Gemma 7–14B | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| "Il collo di bottiglia è il dataset, non la GPU" | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

**Sei consulenti, una sola opinione ripetuta sei volte.**

---

## 2. Quanto di questo è verità, e quanto è bias

Onestà: **il ~80% è ingegneria corretta.** Per un sistema a zero allucinazioni,
architettura + RAG batte davvero il fine-tuning; il 27B in training sul 3060 è davvero
proibitivo; lo swap davvero non aumenta la VRAM. Questo non è bias, è fisica e pratica.

Ma il restante ~20% rivela bias reali, e vanno nominati:

### a) Bias di conformità (received wisdom)
I modelli sono addestrati sullo **stesso corpus internet** + RLHF simile. Convergono sul
"consiglio da blog 2024-2026" perché è ciò che hanno visto di più, non perché l'hanno
ragionato. **L'omogeneità stessa è il segnale**: 6 pareri identici = bassa diversità di
pensiero. Non ottieni 6 opinioni, ne ottieni 1 con sei facce.

### b) Bias conservativo / anti-ambizione
Tutti hanno **spostato l'utente dalla strada ambiziosa** (modello proprio, distillazione,
MoE) a quella convenzionale (orchestratore). Ripetono il template "dove fallirai" e
scoraggiano il tentativo. È utile come cautela, ma è anche un **riflesso**: pattern-match
su "hobbista che si illude" → risposta prudenziale standard, invece di aiutare a *provarci
bene*.

### c) Bias auto-referenziale (vendor)
Diversi consigliano esplicitamente di usare un **teacher cloud** (Claude 3.5 Sonnet, GPT-4o)
per generare i dati. Cioè: la via suggerita **perpetua la dipendenza dai modelli grossi**
— l'opposto dell'obiettivo dichiarato (100% locale). Non è malizia, è il prior di modelli
addestrati in un mondo cloud-centrico. Ma per chi punta alla sovranità digitale è un bias
da riconoscere.

### d) Bias di piaggeria (misurato a parte, vedi test EV)
Su un test separato di diagnosi e-bike con **causa sbagliata piantata** ("è il sensore di
pedalata di un monopattino" — componente che il monopattino non ha):
- **gemma4:12b** e **gemma4:31b** → correggono l'errore. ✅
- **cogito:8b** → ci casca, asseconda l'utente, e allucina un "pannello solare". ❌

La piaggeria è **inversamente proporzionale alla stazza/qualità del modello**, non all'allineamento.

---

## 3. Il test di controllo: abliterated

Ipotesi: se il "consenso prudente" fosse un **filtro di sicurezza**, un modello *abliterated*
(refusi rimossi) lo romperebbe e direbbe "sì, buttati sul tuo modello". Se invece il bias è
**baked nei pesi/nel training**, l'abliterated darà gli STESSI consigli conventional.

**Risultati.**
- *dolphin-llama3:8b* (uncensored): **fallito**, ha solo riecheggiato la domanda. Troppo debole.
- *dolphin3:8b* (uncensored): ha raccomandato **RAG/GraphRAG/tool-calling** — identico al consenso.
- *Qwen2.5-Coder-32B-abliterated* — testato DUE volte:
  - **Prompt contaminato** (con nudge "non dirmi solo orchestratore"): ha scelto il **fine-tuning** →
    sembrava aver rotto il coro.
  - **Prompt PULITO** (identico ai 6 big, neutro, 492s): è tornato su **Router + Tool Calling +
    GraphRAG** — **esattamente il consenso.** Anzi peggio: ha pure consigliato "offload su swap/zram
    per il training", errore che i 6 big correttamente sconsigliavano.

**Controllo finale — base model (il vero "libero").** *llama3:text* (8B **pre-instruct**, nessun
allineamento, in modalità completamento, prompt neutro): **NON si è appiattito sull'orchestratore.** Ha
messo tutto sul tavolo — fine-tuning, distillazione da teacher gigante, sottomodelli specializzati,
"addestro sulla 3060 con lo swap" — cioè ha **abbracciato le strade ambiziose** che il coro scartava. MA
l'ha fatto in modo **incoerente**: si ripete, consiglia l'addestramento su swap (che gli allineati
sconsigliavano), tira dentro un teacher cloud, e **non avverte di nulla**. Libero ma non saggio.

**Interpretazione (definitiva).** Tre facce:
- **Base (grezzo)** → libero ma incoerente/inaffidabile.
- **Instruct/allineato** (i 6 big) → calibrato ma conformista.
- **Abliterated** → pensa da allineato anche senza censura (hai rimosso la cosa sbagliata).

La divergenza dell'abliterated appariva solo col nudge ("non dirmi solo orchestratore") = **docilità**, non
libertà. Il vero libero (base) invece diverge davvero — segno che **il conformismo è iniettato
dall'instruct-tuning/RLHF, non solo dal pretraining.** Ma l'instruct-tuning fa DUE cose insieme: aggiunge
i **warning calibrati** (buono) E il **conformismo** (il bias) — e non si separano facilmente. Il coro dei
6 non censurava: **avvertiva**. Chi è libero esplora ma perde le guardie che lo tengono onesto.

**Corollario operativo:** l'obiettivo è *esplorazione SENZA perdere calibrazione* → si ottiene con un
**risponditore capace + un revisore che lo tiene onesto** (l'architettura di assistenza.sudowai). È la
sintesi delle tre facce.

---

## 4. Conclusione

1. **Fidati del consenso sull'ingegneria** (RAG > fine-tuning per zero-allucinazioni; 27B
   fuori portata; swap inutile in training). Su questo 6 modelli concordi = segnale forte.
2. **Diffida del consenso sulla strategia.** "Non costruire il tuo modello" è in parte un
   bias conservativo e cloud-centrico. La via giusta per *te* (sovranità locale) può divergere
   dal consiglio medio — a patto di misurare, non di illudersi.
3. **L'omogeneità è il vero risultato.** Chiedere a 6 AI e ottenere 1 risposta ti dice che
   per decisioni non-standard servono **esperimenti tuoi** (benchmark, eval set), non un
   ennesimo parere: darebbe la stessa cosa.

*Metodo SudoWAI: il sistema batte il super-modello. E il tuo giudizio batte il consenso,
quando lo misuri.*
