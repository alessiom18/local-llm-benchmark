# I benchmark (fai-da-te) mentono
### Cosa abbiamo imparato provando a misurare *sul serio* decine di modelli di AI in locale

*Di [SudoWAI](https://sudowai.com) — AI in locale, senza Big Tech · Livorno. Parte 2 della ricerca [«Non esiste il modello migliore»](../ARTICOLO.md).*

---

## Il problema
Volevamo una risposta pratica: *quale modello di AI conviene usare, per ogni compito, sul nostro hardware?* Così abbiamo costruito un banco di prova con **decine di modelli** (tra originali, varianti e fusioni) e i **compiti veri** del nostro gestionale. Alla prima classifica ci siamo quasi cascati: un modello da 3 miliardi di parametri in testa, uno da 31 in fondo. **Impossibile.** Il benchmark era rotto — e non ce ne saremmo accorti se non avessimo guardato dentro i numeri.

Ecco i tre modi in cui un benchmark casalingo **ti inganna**, e come li abbiamo neutralizzati.

## Trappola 1 — Misurare la forma, non la sostanza
I controlli automatici facili (*"è un JSON valido? c'è la funzione? il testo è lungo giusto?"*) sono cose che **anche un modello piccolo fa benissimo**. Risultato: **104 risposte su 115 prendevano il massimo dei voti.** Tutti "bravissimi", nessuna differenza. Se un test dà a tutti 10, **il test è rotto.**

## Trappola 2 — Penalizzare il migliore per un limite tecnico
Peggio: i modelli più bravi venivano **puniti**. Scrivevano risposte più ricche e complete che, superando un limite di lunghezza impostato male, risultavano "tagliate" e quindi "incomplete". Abbiamo trovato **36 risposte troncate** — quasi tutte dei modelli migliori. Un controllo ingenuo, di fatto, **premiava chi rispondeva meno.** Le abbiamo rifatte con spazio abbondante: una risposta tagliata non è una risposta sbagliata.

## Trappola 3 — Fidarsi di un solo giudice
Per i compiti "aperti" (un consiglio, una ricetta, un sito) non basta un controllo automatico: serve valutare la **qualità**. Ma anche qui c'è un tranello: **chi giudica?** Abbiamo usato un **modello giudice che valuta alla cieca** (voto 1–5, senza sapere chi ha scritto). E come riprova ne abbiamo usati **tre diversi**. Scoperta interessante: **i tre giudici non erano d'accordo sul "primo assoluto"**, pur concordando su chi stava in alto e chi in basso. Morale: **anche la scelta del giudice è una scelta che pesa.** Un benchmark con un solo giudice è, di nuovo, un'illusione di precisione.

## Bonus — Il "ragionamento" (thinking) conviene? Quasi mai
Molti modelli hanno una modalità "pensa ad alta voce prima di rispondere". L'abbiamo provata accesa e spenta. Sui compiti concreti e strutturati **peggiora quasi sempre**: rallenta e spesso **rompe il formato**. Un caso limite: un modello passava dall'**80% di risposte corrette allo 0%** con il ragionamento acceso (produceva testo che non stava più nel formato richiesto). Va tenuto **spento** per il lavoro pratico; semmai serve solo per i compiti creativi/strategici.

---

## Perché ve lo raccontiamo
Perché il mondo dell'AI è pieno di classifiche e "record" che, guardati da vicino, misurano poco. Noi facciamo una cosa diversa: **misuriamo sui compiti veri, correggiamo i nostri stessi errori di metodo, e pubblichiamo tutto** — codice, dati grezzi, anche ciò che non ha funzionato. È lo stesso rigore con cui costruiamo **SmartShop** e gli assistenti che girano **in locale**, a casa del cliente, senza mandare i dati nel cloud di nessuno.

*Dati e codice: [github.com/alessiom18/local-llm-benchmark](https://github.com/alessiom18/local-llm-benchmark) · SudoWAI, Livorno.*
