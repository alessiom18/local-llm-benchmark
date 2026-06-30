<!-- BOZZA ARTICOLO — i segnaposto {{...}} si riempiono coi dati a benchmark finito. -->
# Non esiste "il modello migliore"
### Cosa abbiamo imparato facendo girare 9 modelli AI in locale, su hardware normale, sui compiti veri di un gestionale

*Di [SudoWAI](https://sudowai.com) — software e AI in locale, senza Big Tech, Livorno.*

---

## In due righe
Abbiamo messo alla prova 9 modelli di intelligenza artificiale **interamente in locale** (nessun cloud) sui compiti reali del nostro gestionale **SmartShop**: classificare richieste, estrarre menù, scrivere codice, generare siti, dare consigli commerciali. La conclusione è netta e contro-intuitiva: **non vince sempre lo stesso modello, e il più grosso non è il migliore.** Quello che conta davvero è **come gestisci le risorse** — quale modello mandi a fare cosa.

---

## Perché l'abbiamo fatto
A SudoWAI tutto gira **in locale**, su hardware nostro, senza dipendere da OpenAI o da nessun cloud. La domanda pratica era: *con una scheda video normale (una RTX 3060 da 12GB) e qualche PC, quale modello conviene usare per ogni cosa?* Invece di fidarci delle classifiche online (fatte su benchmark accademici lontani dal lavoro reale), ci siamo costruiti **il nostro banco di prova sui nostri compiti veri**.

**Hardware del test:** {{HW}} — niente di esotico, proprio il tipo di macchina che può stare nel retro di un negozio.

**I 9 modelli:** {{MODELLI}}.

**I compiti (13):** classificazione di richieste in linguaggio naturale, estrazione di un menù in dati strutturati, riconoscimento allergeni, configurazione del gestionale, consigli commerciali, ricette, scrittura di codice, revisione di codice, copywriting, generazione di siti web. Tutti compiti **veri** che SmartShop chiede all'AI ogni giorno.

---

## La prima lezione (a nostre spese): i benchmark ingenui MENTONO
Il primo giro ci ha dato una classifica **assurda**: un modello da 3 miliardi di parametri primo, uno da 31 miliardi ultimo. Impossibile.

Il motivo è una trappola in cui cascano tantissimi benchmark fai-da-te: **misuravamo la forma, non la sostanza.** I nostri controlli automatici verificavano *"è un JSON valido? c'è la funzione? il testo è nella lunghezza giusta?"* — cose che **anche un modello piccolo fa benissimo**. Così tutti prendevano il massimo dei voti, e i modelli migliori venivano perfino **penalizzati**: scrivevano risposte più ricche che un controllo ingenuo bocciava (un sito più completo veniva tagliato dal limite di lunghezza e risultava "non finito").

**Due correzioni** hanno cambiato tutto:
1. **Niente penalità per il limite tecnico.** Decine di risposte erano semplicemente *troncate* perché avevamo dato pochi "token" di spazio. Le abbiamo rifatte con spazio abbondante: una risposta tagliata non è una risposta sbagliata.
2. **Un giudice vero per la qualità.** Per i compiti aperti (consigli, ricette, codice, siti) un *controllo automatico* non basta. Abbiamo usato un **modello giudice** che valuta ogni risposta **alla cieca**, con una rubrica, dando un voto da 1 a 5 — e, come riprova, **il modello risultato migliore ha rifatto da giudice** per controllare che la classifica reggesse. Abbiamo anche verificato a mano un campione dei giudizi.

> Questa parte, da sola, è la lezione più importante: **se un benchmark dà a tutti 10, il benchmark è rotto.**

---

## I risultati
{{TABELLA_CLASSIFICA}}

{{GRAFICO_QUALITA}}

{{GRAFICO_VELOCITA}}

**Il quadrante qualità-vs-velocità** — qui si vede tutto in un colpo: in alto a destra (bravi *e* veloci) ci finiscono i modelli **contenuti**, non i giganti.

{{GRAFICO_QUADRANTE}}

### Chi vince su cosa
Il punto chiave: **modelli diversi vincono compiti diversi.**
{{TABELLA_PER_CATEGORIA}}

{{COMMENTO_RISULTATI}}

---

## Thinking sì o no? E lo stile "telegrafico"?
Abbiamo provato anche due varianti:
- **Ragionamento esplicito ("thinking") acceso vs spento.** {{ESITO_THINKING}} *(anticipazione dai nostri test precedenti: sui compiti strutturati il "thinking" tende a rallentare e a volte rompe il formato JSON; aiuta solo sui compiti aperti/strategici.)*
- **Stile "caveman" (risposte telegrafiche)** sui modelli più grossi. {{ESITO_CAVEMAN}}

---

## La tesi vera: non un cervello gigante, ma un buon direttore d'orchestra
Da tutto questo esce la nostra convinzione, che è anche il modo in cui costruiamo i prodotti SudoWAI:

> **Il valore non è nel modello più grande. È nel SISTEMA che manda il modello giusto a fare la cosa giusta.**

Un modello piccolo e veloce per capire e smistare le richieste; uno specializzato per il codice; uno per la visione (foto → prodotti); uno "stratega" solo quando serve davvero ragionare. È così che un setup **contenuto** rende più di un singolo gigante generico — costando una frazione di energia e potendo girare **in locale**, in un negozio, senza mandare i dati di nessuno nel cloud.

### E i computer "da buttare"?
Stiamo portando questa idea all'estremo: una **flotta** di PC modesti — anche vecchi, anche recuperati — dove **ogni macchina fa una cosa sola** (un ruolo, un agente). Non è un solo cervello potente: è una squadra di nodi specializzati coordinati da un direttore. *(Sezione in arrivo, con i test reali su hardware di recupero.)* {{SEZIONE_FLOTTA}}

---

## Dove stiamo andando (architettura)
I prossimi passi, scelti **in base a questi dati**:
- **Routing intelligente:** un modello-router leggero che, letta la richiesta, sveglia il modello migliore per quel compito (lo dimostrano i risultati qui sopra).
- **Fusione di modelli (model merging):** unire i due modelli che vincono su compiti complementari in **un unico modello compatto** che le sa fare entrambe, senza diventare più lento.
- **Decodifica speculativa:** ottenere la qualità di un modello grande alla velocità di uno piccolo, dove la memoria lo consente.

---

## Riproducibilità
Tutto il codice del banco di prova è qui: i compiti, lo script che esegue i modelli, il giudice e i grafici. Chiunque può rifare i test sul proprio hardware. {{LINK_REPO}}

*SudoWAI — Livorno. SmartShop (gestionale con AI locale), Serena (assistente WhatsApp), M.A.R.C.O. — tutto self-hosted, niente Big Tech.*
