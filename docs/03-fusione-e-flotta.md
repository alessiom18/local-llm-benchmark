# Fondere i modelli, e farli lavorare in squadra
### Un esperimento onesto: dare "nuove abilità" a un modello, e far collaborare due computer

*Di [SudoWAI](https://sudowai.com) — AI in locale, senza Big Tech · Livorno. Parte 3 della ricerca [«Non esiste il modello migliore»](../ARTICOLO.md).*

---

## La flotta: due computer meglio di un supercomputer
La nostra tesi è che **il valore non è nella macchina più potente, ma nel sistema** che usa bene le risorse. L'abbiamo messa in pratica: due computer normali che **collaborano in rete**.

- **MARCO** — una RTX 3060 (12GB), il nodo di casa: orchestrazione, compiti in tempo reale, fusioni.
- **NITRO** — una scheda video di fascia superiore, in **un altro luogo**, collegata in modo sicuro e cifrato (prima via VPN privata, poi in rete locale via cavo).

Il risultato pratico: mentre un computer faceva una parte della ricerca, l'altro ne faceva un'altra. **Due notti di lavoro in una.** NITRO ha macinato i modelli grossi (24-26 miliardi di parametri) che sul nodo piccolo arrancavano, mentre MARCO lavorava alle fusioni. Nessun data center, nessun cloud: **due macchine, in due stanze, che si passano il lavoro.**

È esattamente il modello che portiamo ai clienti: non un unico "cervellone", ma **una squadra di nodi**, ognuno con il suo compito — e domani anche computer modesti, recuperati, possono aggiungersi come nodi specializzati.

## Fondere i modelli: dare nuove abilità
La seconda idea: invece di *scegliere* un modello, **fonderne due o più in uno solo** — mescolarne i pesi (le "sinapsi") per combinare le competenze. L'equivalente di dare a un bravo cuoco anche le ricette di un pasticcere: **nuove abilità, senza diventare più lento.** Esistono ricette diverse (SLERP, TIES, DARE, frankenmerge), tutte senza bisogno di ri-addestrare da zero.

## Cosa è andato storto (e perché lo raccontiamo)
Qui la ricerca aperta mostra il suo valore: **pubblichiamo anche i fallimenti.** Il primo tentativo di fusione **è degenerato** — i modelli fusi producevano testo incomprensibile, mentre i "genitori" funzionavano bene. Non un piccolo calo di qualità: **spazzatura.**

Indagando, la causa non era l'idea, ma gli **strumenti troppo "di frontiera"**: alcune librerie all'ultimissima versione calcolavano la fusione in modo errato. La lezione, spesso taciuta nei post entusiasti: **fondere i modelli non è magia gratis.** Serve la ricetta giusta *e* strumenti stabili, altrimenti si rompe ciò che funzionava.

Abbiamo riprovato anche con **librerie in versione stabile**: e la fusione **si è rotta di nuovo**. Segno che il problema è più profondo — la nostra ipotesi attuale è un **disallineamento dei "vocabolari"** tra i due modelli di partenza (parlano la stessa lingua ma con dizionari leggermente diversi, e mescolarli confonde il risultato). È un **problema aperto**, e lo lasciamo scritto così com'è: la prossima volta proveremo a fondere modelli con lo **stesso identico dizionario** (per esempio due varianti dello stesso modello base), dove la fusione ha molte più probabilità di riuscire.

Nessun titolo trionfale, quindi. Ma è proprio questo il punto: **una ricerca seria si giudica anche da come racconta ciò che non è filato liscio.** Chi ti promette solo successi, di solito, non ha mai davvero provato.

## Perché conta per te (che hai un'attività)
Non ti servono i dettagli tecnici. Ti serve sapere una cosa: **noi non vendiamo fumo.** Proviamo, misuriamo, sbagliamo, correggiamo — e mettiamo tutto in chiaro, dati e codice. È la stessa serietà con cui costruiamo **SmartShop** e gli assistenti che girano **in locale**, con i tuoi dati che restano a casa tua.

*Dati e codice: [github.com/alessiom18/local-llm-benchmark](https://github.com/alessiom18/local-llm-benchmark) · SudoWAI, Livorno.*
