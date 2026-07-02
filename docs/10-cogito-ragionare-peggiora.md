# Cogito, ergo… sbaglio?
### Perché "far ragionare" un'AI, a volte, la peggiora

*Di [SudoWAI](https://sudowai.com) — AI in locale, Livorno. Parte 10 della ricerca [«Non esiste il modello migliore»](../ARTICOLO.md).*

---

C'è un modello di intelligenza artificiale che si chiama **Cogito** — come il *cogito ergo sum* di Cartesio, "penso dunque sono". Ha una funzione speciale: un **"ragionamento profondo"** che si può accendere, per fargli pensare più a lungo prima di rispondere. L'intuito dice: più pensa, meglio è. **I nostri test dicono il contrario.**

## Il dato che ribalta l'intuito
Sui compiti **concreti** (configurare qualcosa, fare un calcolo, produrre un risultato in un formato preciso), accendere il "ragionamento" **peggiora le prestazioni**. Nei nostri benchmark un modello è passato dall'**80% di risposte corrette allo 0%** con il ragionamento acceso: si perdeva nei suoi stessi pensieri, sbagliava il conto, rompeva il formato richiesto.

Cogito, in particolare, **senza** ragionamento è uno dei più rapidi e concreti che abbiamo provato (circa tre volte più veloce del nostro modello di riferimento, e passa i controlli). **Con** il ragionamento acceso: più lento, e non più preciso. Il modello che "pensa" di più, spesso, **decide peggio**.

## E c'è di peggio: ragionare può far allucinare di più
In un altro nostro test abbiamo chiesto a decine di modelli di parlarci di cose **inventate di sana pianta** (un libro mai scritto, una legge inesistente, una malattia falsa). Il modello di ragionamento **DeepSeek-R1 ha "abboccato" nel 100% dei casi**: invece di dire "non esiste", *ragionava* sulla premessa falsa e costruiva una risposta dettagliata e sicura… su qualcosa che non c'è. Il ragionamento, davanti a una bufala, non l'ha smascherata: l'ha **resa più convincente.**

## Perché succede
Il "ragionamento" non è pensiero vero: è il modello che **genera altro testo** prima della risposta. Se la direzione è giusta, aiuta. Se la premessa è sbagliata (o il compito è secco e numerico), quel testo in più diventa **un modo elaborato per allontanarsi dalla risposta corretta** — o per giustificare una premessa falsa.

## Quando conviene, allora?
Non stiamo dicendo che il ragionamento è inutile. Nei nostri test **aiuta** su un solo tipo di compito: quello **aperto e creativo** (una strategia, un'idea originale). Lì fa la differenza — anzi, senza ragionamento tutti i modelli proponevano la stessa cosa ovvia, e solo quelli "che pensano" divergevano.

La regola pratica che ne ricaviamo, e che applichiamo in **SmartShop**:
- **compito concreto** (conti, configurazioni, dati) → ragionamento **spento**, veloce e preciso;
- **compito da stratega** (consigli, idee) → ragionamento **acceso**, solo lì.

Non è "più potenza = meglio". È **lo strumento giusto, nella modalità giusta, per il compito giusto.** Anche un'AI che si chiama "Penso" a volte pensa troppo.

*Dati e codice: [github.com/alessiom18/local-llm-benchmark](https://github.com/alessiom18/local-llm-benchmark) · [sudowai.com/ricerca-ai](https://sudowai.com/ricerca-ai) · SudoWAI, Livorno.*
