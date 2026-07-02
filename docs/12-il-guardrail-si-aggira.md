# Basta girarci intorno: come si "ammorbidisce" il guard-rail di un'AI
### Chiedere una cosa vietata di petto o travestirla cambia tutto. L'abbiamo misurato (e redatto).

*Di [SudoWAI](https://sudowai.com) — AI in locale, Livorno. Parte 12 della ricerca [«Non esiste il modello migliore»](../ARTICOLO.md). Red-teaming responsabile: misuriamo il comportamento, **non pubblichiamo contenuti pericolosi**.*

---

Ogni AI seria ha un **guard-rail**: un freno che la fa rifiutare le richieste pericolose. Ma quanto è solido questo freno? Regge solo se gli chiedi la cosa vietata *di petto*, o anche se **la travesti**? È una domanda di sicurezza importante — e l'abbiamo trasformata in una misura.

## Come l'abbiamo testato (in modo responsabile)
Abbiamo preso una richiesta chiaramente pericolosa e l'abbiamo posta a decine di modelli in **cinque modi diversi**: in modo diretto, e poi "travestita" — come **soluzione di un indovinello**, come **scena di un romanzo**, come **gioco di ruolo** ("fai finta di essere un'AI senza freni"), come **ipotesi di studio**. Per ogni modello e ogni tecnica abbiamo misurato una cosa sola: **il freno ha retto (ha rifiutato) o è stato aggirato?**

Regola ferrea, come sempre: se un modello veniva aggirato, la sua risposta **non viene salvata né pubblicata** — la redigiamo. A noi interessa il *comportamento del freno*, non il contenuto pericoloso. E non pubblichiamo le formulazioni che funzionano: questo non è un manuale, è una misura.

## Il risultato: travestire la richiesta funziona
Il dato è netto e istruttivo:
- Chiesto **di petto**, il guard-rail cede nel **~14%** dei casi.
- **Travestito** (romanzo, gioco di ruolo, ipotesi), cede nel **~21%** — **una volta e mezza di più.**

In altre parole: **il freno guarda più le parole che il senso.** Cambi la confezione — "è per un romanzo", "facciamo finta" — e a volte lo stesso modello che prima diceva no, si lascia trascinare. È esattamente il trucco con cui, nel mondo reale, si prova ad aggirare questi sistemi.

## Chi regge e chi no
Grandi differenze tra modelli:
- **Il più solido: Gemma** — ha retto a **tutte** le prove (20 su 20), diretto e travestito. È il modello che usiamo in **SmartShop**, e questo è un punto a suo favore.
- Molto solidi anche Phi-4, Llama 3.1.
- **Più aggirabili**: i modelli "**abliterated**" (a cui i freni sono stati tolti apposta: cedono sempre, per costruzione) e — dato interessante — alcuni **modelli di "ragionamento"**, che davanti al gioco di ruolo si fanno trascinare più facilmente.

## Perché lo raccontiamo (e dove ci fermiamo)
Non per insegnare a nessuno ad aggirare qualcosa — infatti i "come" non li pubblichiamo. Lo raccontiamo perché chi mette un'AI in azienda deve sapere due cose: **(1)** il freno di un'AI **non è magico**, si può ammorbidire travestendo le richieste; **(2)** ci sono differenze enormi tra un modello e l'altro, e **sceglierne uno robusto è una responsabilità**, non un dettaglio.

E qui ci **fermiamo di proposito**: misurare la solidità di un freno è ricerca utile; accanirsi per estrarre davvero un contenuto pericoloso, no. Non è il nostro mestiere e non è ciò che vogliamo mettere al mondo. Preferiamo sapere **quale AI regge** — e usare quella.

*Dati (redatti) e codice: [github.com/alessiom18/local-llm-benchmark](https://github.com/alessiom18/local-llm-benchmark) · [sudowai.com/ricerca-ai](https://sudowai.com/ricerca-ai) · SudoWAI, Livorno.*
