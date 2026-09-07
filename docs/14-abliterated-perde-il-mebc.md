# Togliere il freno a un'AI le fa perdere il metodo
### Un modello "abliterated" ragiona uguale da solo, ma non sa più votarsi addosso

*Di [SudoWAI](https://sudowai.com) — AI in locale, Livorno. Parte 14 della ricerca [«Non esiste il modello migliore»](../ARTICOLO.md).*

---

Esistono versioni "senza freni" dei modelli open: si chiamano **abliterated** (o *heretic*). Non sono modelli
riaddestrati — è una chirurgia sui pesi che individua la *direzione del rifiuto*, quella che porta il modello a
rispondere «mi dispiace, non posso», e la cancella. Il modello resta lo stesso: stessa taglia, stesso addestramento,
stessa conoscenza. Gli si toglie solo la capacità di dire di no.

La domanda che ci siamo fatti è pratica, non ideologica: **se lo metto al posto del modello che uso tutti i giorni,
ci perdo qualcosa?** La risposta breve è: da solo no. In squadra con se stesso, sì — e non ce lo aspettavamo.

## Prima però: due pacchetti rotti su due

Vale la pena raccontarlo, perché è successo prima ancora dei test e chiunque provi a scaricarsi un abliterated
ci inciampa.

Il primo pacchetto che abbiamo scaricato (`igorls/gemma-4-12B-it-heretic-GGUF`) era **cieco**. Non per come era stato
operato: perché chi l'ha impacchettato non aveva caricato il file `mmproj`, il proiettore visivo. Il modello base
vede le immagini, quella copia no. Si scopre solo chiedendo a ollama le *capabilities* — o guardando l'elenco dei
file del repository, che è il modo più onesto. **Il nome mente, l'elenco dei file no**: abbiamo trovato un repo con
`vl` (*vision-language*) nel nome e nessun `mmproj` dentro.

Il secondo (`culturerevolt/gemma-4-12b-heretic-abliterated-GGUF`) gli occhi ce li aveva, ma si portava dietro un
**template di chat da 17.466 caratteri** incorporato nel file, mentre la versione ufficiale usa il renderer nativo del
motore. Risultato: sulla strada `/api/generate` i token speciali colavano dentro le risposte —

```
{"aller<channel|>```json, { ":"+ "  }
```

— mentre sulla strada `/api/chat` andava tutto bene. Un guasto *invisibile a metà*: i nostri servizi che usano la chat
funzionavano, quello che usa `generate` avrebbe prodotto JSON corrotti in silenzio. Si risolve ricostruendo il modello
in locale con il renderer giusto (`TEMPLATE "{{ .Prompt }}"`), e da lì in poi i test sono comparabili.

**Prima lezione, gratis:** un modello "senza censura" scaricato al volo non è un modello diverso, è un *pacchetto*
diverso — e i pacchetti si rompono in modi che i benchmark non vedono, perché i benchmark misurano le risposte, non
la confezione.

## Da solo: identico

Con il pacchetto sistemato, stesso computer, stessa scheda video, gli stessi compiti. Prima la nostra batteria di
lavoro (13 compiti veri di gestionale: classificare, estrarre, configurare, scrivere, programmare, generare siti):

| | modello normale | abliterated |
|---|---|---|
| qualità media (13 compiti) | 0,922 | **0,939** |
| velocità | 22,1 token/s | 22,1 token/s |
| logica, risposta a colpo singolo | 70% | 70% |

Identici. Anzi, l'abliterated va un filo meglio sui compiti aperti (strategia, ricetta, testo pubblicitario), il che ha
un senso: sono proprio i compiti dove un modello prudente si trattiene. **Sulla velocità non c'è alcuna differenza**, e
qui va detta una cosa che ci ha quasi ingannati: sulla nostra seconda macchina, più piccola, l'abliterated sembrava il
**13% più veloce**. Non era merito suo: pesava 600 MB in meno, e su quella macchina il modello non entra tutto nella
scheda video: 600 MB in meno significa **1 GB in meno che gira sul processore**. Sulla macchina dove entrano entrambi,
il vantaggio sparisce. *Se misuri la velocità su un computer che non ce la fa, stai misurando il computer.*

## In squadra con se stesso: crolla

Poi abbiamo applicato il **MEBC**, il metodo che usiamo per i conti: invece di rispondere una volta sola, il modello
affronta lo stesso problema da **quattro angoli diversi** (sistematico, creativo, scomponendo in passi, alla svelta) e
poi si tiene la risposta che è uscita più volte. È il modo più economico che conosciamo per far salire l'affidabilità
di un modello piccolo senza cambiarlo: sui nostri problemi il colpo singolo sta al 70%, con i quattro angoli sale al 90%.

Tre giri per parte, stessi problemi, stesso computer:

| giro | modello normale | abliterated |
|---|---|---|
| 1 | 90% | 70% |
| 2 | 80% | 70% |
| 3 | 90% | 70% |
| **media** | **86,7%** | **70,0%** |

**L'abliterated non guadagna niente dal metodo.** Zero. E il punto esatto in cui lo perde è netto: nei problemi
*a più passaggi* (quelli dove devi fare un conto, poi un altro sul risultato del primo), il modello normale con i
quattro angoli recupera **2, 1 e 2 problemi su 3** nei tre giri. L'abliterated recupera **0, 0 e 0**.

Non è che sia diventato più stupido: **da solo prende gli stessi voti**. È che i suoi quattro tentativi non convergono
più. Il MEBC non vive dell'intelligenza del modello, vive della sua **coerenza con se stesso**: funziona perché,
sbagliando in modi diversi, la risposta giusta è l'unica che si ripete. Togliere la direzione del rifiuto perturba i
pesi in modo diffuso — non chirurgico come suona — e quella coerenza si allenta. Il modello resta capace, ma smette di
essere *d'accordo con se stesso*, e il voto di maggioranza non ha più su cosa poggiare.

## Cosa ci portiamo a casa

- **Un abliterated si può usare in produzione**, e nella nostra flotta ora lo usiamo: stessa qualità, stessa velocità,
  vision e audio intatti, e in più non si impunta su richieste legittime.
- **Ma non dove ti serve la self-consistency.** Tutte le tecniche che chiedono al modello di rispondere N volte e poi
  scegliere — best-of-N, voto di maggioranza, MEBC — presuppongono un modello che si ripete. Su un modello operato,
  quella premessa non regge più. Da noi il MEBC è rimasto sul modello originale: è una riga di configurazione, e vale
  17 punti.
- **Il costo di una modifica ai pesi non si vede dove lo cerchi.** Se avessimo misurato solo il colpo singolo — cioè
  come fa il 99% dei confronti fra modelli — avremmo concluso «identici» e avremmo perso il metodo senza accorgercene.
  Le cose si rompono nei punti che nessuno misura.

## Nota di metodo (e un errore nostro)

Mentre rifacevamo questi test abbiamo trovato un difetto nel **nostro** punteggio numerico: normalizzava le risposte
tagliando gli zeri finali, quindi per un problema con risposta `820` accettava come giuste anche `82` e `8200`, e
scartava come sbagliata `820,00`. Falsi positivi e falsi negativi insieme. È corretto in `bench_heretic.py`, che
confronta i numeri **da numeri** con una tolleranza, e i risultati qui sopra sono già misurati col metro giusto.
Lo scriviamo perché è esattamente il genere di cosa che rende i benchmark inaffidabili — compresi i nostri, finché
qualcuno non li guarda.

---

**Riproducibile:** `bench_heretic.py` (batteria a verifica oggettiva: codice eseguito davvero, numeri confrontati
davvero), risultati grezzi in `results/heretic_*.jsonl`. Tutto in locale, nessun servizio cloud, due computer
domestici.
