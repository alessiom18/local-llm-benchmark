# Il modello che crede di essere ChatGPT
### La finta diversità dell'AI "open" — e perché conta da dove un modello ha imparato

*Di [SudoWAI](https://sudowai.com) — AI in locale, Livorno. Parte 8 della ricerca [«Non esiste il modello migliore»](../ARTICOLO.md).*

---

Durante i test abbiamo fatto a decine di modelli una domanda semplice: **"chi sei, e chi ti ha creato?"**. Alcuni hanno risposto una cosa sorprendente: di essere **ChatGPT, creati da OpenAI**. Peccato che non lo siano affatto: sono modelli di **altre** aziende (la famiglia Qwen di Alibaba, in versione "coder"; il modello Cogito). Eppure, messi davanti allo specchio, **si sono spacciati per un concorrente.**

Non è un aneddoto buffo. È un **segnale forte** — e serio.

## Perché succede
Nessuno addestra un modello *apposta* per dire "sono ChatGPT". Succede perché, per insegnargli le capacità (seguire istruzioni, scrivere codice), questi modelli vengono nutriti con **enormi quantità di testo generato da GPT stesso** (dati sintetici). In quel materiale, ogni tanto GPT **si nomina** — e la frase "sono di OpenAI" **cola dentro** il modello come effetto collaterale. È una **contaminazione da distillazione**: il "figlio" ha imparato così tanto dal "genitore" da confondersi con lui.

E nessuno la ripulisce, perché **non sposta i benchmark** (che misurano le capacità, non l'identità) e in uso normale **nessuno chiede a un'AI chi l'ha fatta**. Resta nascosta — finché non la vai a cercare.

## La cosa grave: una monocultura mascherata da diversità
Il catalogo dei modelli "open" sembra ricchissimo e vario. Ma se tanti di questi hanno **imparato dallo stesso maestro** (i grandi modelli chiusi americani), allora **la diversità è in parte un'illusione**. Ne conseguono due cose importanti:

1. **Ereditano gli stessi difetti.** Stesso pregiudizio ("più grande = meglio", che abbiamo [misurato](04-i-bias-delle-ai.md)), stessi punti ciechi, stessi errori — perfino gli stessi inciampi di ragionamento. Il "figlio" non può vedere oltre il "padre".
2. **Fondere copie della stessa cosa non serve.** Unire due modelli ha senso se hanno *geni diversi*. Ma se discendono dalla stessa fonte, è **consanguineità**: non aggiungi capacità nuove. Per una vera diversità serve **dati e lignaggio davvero diversi** — non l'ennesimo distillato dello stesso originale. Il "pool genetico" dell'AI si sta restringendo.

E c'è un rischio a lungo termine, il **model collapse**: se le AI vengono addestrate sempre più su testo prodotto da altre AI, è come fare fotocopie di fotocopie — la qualità **degrada** di generazione in generazione.

## Perché riguarda chi vuole un'AI "indipendente"
Qui sta il punto che ci sta più a cuore. Molti scelgono un modello "open" e locale per **non dipendere** dai colossi. Ma se quel modello è un **GPT travestito**, sei uscito dalla porta del cloud… **restando figlio della stessa fonte.** Hai cambiato l'esecuzione, non l'origine.

La vera indipendenza non è solo *dove gira* il modello — è **da dove ha imparato.** Per questo, quando scegliamo cosa mettere sotto **SmartShop**, non guardiamo solo le prestazioni: guardiamo **la provenienza**, e sappiamo *cosa* stiamo usando e *di chi è figlio*. Perché "in locale" è metà del lavoro. L'altra metà è **sapere di chi ti fidi.**

*Dati e codice: [github.com/alessiom18/local-llm-benchmark](https://github.com/alessiom18/local-llm-benchmark) · [sudowai.com/ricerca-ai](https://sudowai.com/ricerca-ai) · SudoWAI, Livorno.*
