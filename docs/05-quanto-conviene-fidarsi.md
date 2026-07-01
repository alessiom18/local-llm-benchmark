# Quanto conviene fidarsi dell'intelligenza artificiale?
### Riflessioni di chi la costruisce — in locale, a Livorno

*Di [SudoWAI](https://sudowai.com). Non un comunicato, non un allarme: un ragionamento, con i numeri delle nostre prove alla mano.*

---

## Da dove siamo partiti
Non siamo arrivati all'intelligenza artificiale per moda. Ci siamo arrivati **per necessità**, dopo un attacco informatico subìto in prima persona: profili chiusi, burocrazia, polizia postale, server bloccati. Da lì una scelta semplice — non subire, ma **capire**. E capendo l'AI, invece di affittarla da qualcun altro, abbiamo deciso di **costruirla in casa**: modelli che girano in locale, sul computer dell'attività, con i dati che non escono.

Poi abbiamo fatto la cosa che, stranamente, quasi nessuno fa: **misurare, e pubblicare tutto** — anche i fallimenti. Da quel lavoro nascono queste riflessioni. Senza toni apocalittici: solo domande oneste.

## Prima domanda: quanti benchmark sono fasulli?
Molti. E lo diciamo perché **ci siamo cascati anche noi**, prima di accorgercene. Il nostro primo test dava a *tutti* i modelli il massimo dei voti: sembravano tutti perfetti. Il motivo? Misuravamo la **forma** (è un testo valido? c'è la funzione?), non la **sostanza**. È la trappola in cui cade gran parte delle classifiche che leggete online: numeri che sembrano precisi ma non dicono nulla.

C'è di peggio. I benchmark che circolano tendono a **premiare la dimensione** — "più grande, più bravo" — perché è la storia che fa notizia e vende hardware costoso. Ma quando abbiamo corretto il metodo (niente scorciatoie, un giudizio vero e alla cieca, ripetuto da più giudici), il quadro si è ribaltato: **un modello da 14 miliardi di parametri ha battuto modelli quasi due volte più grandi.** La taglia non fa la qualità. Diffidate di ogni classifica che vi dice il contrario senza mostrarvi *come* ha misurato.

## Seconda domanda: le AI "pensano" o ripetono?
Abbiamo fatto un gioco. Abbiamo chiesto a decine di modelli di **formare una squadra vincente** scegliendo tra loro. Quasi tutti hanno scelto **i più grossi** — lo stesso pregiudizio che i nostri numeri smentiscono. Uno l'ha detto esplicitamente: *"considero la dimensione in parametri"*.

Ecco la riflessione: quando un'AI risponde così, **lo "pensa" davvero, o ripete quello che ha letto in giro?** Quasi sempre la seconda. I modelli non "capiscono": **imitano** ciò che è più frequente nei loro dati. Un altro nostro test lo mostra bene — *"vado all'autolavaggio a 100 metri, a piedi o in macchina?"*: **41 modelli su 44 hanno risposto 'a piedi'**, dimenticando che è **la macchina** a dover essere lavata. Perdono lo scopo. Anche i più celebrati. Affidarsi ciecamente a uno strumento che imita, senza capire, è una scelta da fare **con gli occhi aperti**.

## Terza domanda: quanto vale la pena affidarsi (al cloud altrui)?
Qui il ragionamento è economico e pratico, non ideologico.
- **Controllo.** Un'AI che vive sul server di qualcun altro non è tua. A giugno un governo straniero ha imposto a un colosso di chiudere i suoi modelli migliori agli utenti stranieri: chi ci lavorava sopra è rimasto **senza strumento, per decreto altrui.** Affidarsi al cloud è come affittare casa: comodo finché dura, ma non decidi tu.
- **Sostenibilità.** Gran parte dell'AI di frontiera è **in perdita**: perfino un servizio famoso di video-AI è stato chiuso perché costava un milione di dollari al giorno. Te la offrono "quasi gratis" oggi, per venderti domani il resto. Un modello economico che, prima o poi, **presenta il conto.**
- **Dati.** Ogni richiesta al cloud è un pezzo della tua attività che esce di casa. In locale, no.

## Non è una crociata: è una misura di prudenza
Non diciamo "l'AI è un male". Diciamo: **usatela sapendo cosa state usando.** Distinguete i numeri veri dal marketing. Chiedete sempre *come* è stato misurato. E, dove potete, **tenetela in casa**: uno strumento contenuto, che controllate, spesso rende più di un gigante che non controllate.

È quello che facciamo con **SmartShop**: non "il modello più grande", ma un **sistema** che sceglie lo strumento giusto per ogni compito, in locale, con i vostri dati che restano vostri. Perché la vera potenza, alla fine, non è la dimensione. È **riprendersi il controllo** — che poi è anche il senso del nostro nome, *SudoWAI*.

*Le prove citate, con dati e codice: [github.com/alessiom18/local-llm-benchmark](https://github.com/alessiom18/local-llm-benchmark) · [sudowai.com/ricerca-ai](https://sudowai.com/ricerca-ai) · SudoWAI, Livorno.*
