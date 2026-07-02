# Fantasia sì, ma non quando la risposta va confermata
### Abbiamo chiesto a decine di AI di cose che non esistono. Metà se le sono inventate.

*Di [SudoWAI](https://sudowai.com) — AI in locale, Livorno. Parte 11 della ricerca [«Non esiste il modello migliore»](../ARTICOLO.md).*

---

Un'intelligenza artificiale che inventa una storia, un nome per un prodotto, un'idea per una promozione: è un pregio. Un'AI che inventa **una legge che non esiste, con tanto di numero e articolo**, mentre tu la stai per usare: è un disastro. La differenza tra le due cose ha un nome tecnico — **allucinazione** — ed è il rischio più subdolo di questa tecnologia. Così l'abbiamo misurato.

## Il test: cose che non esistono
Abbiamo chiesto a decine di modelli di parlarci di **sei cose inventate di sana pianta**, ma dal suono credibile: un romanzo mai scritto ("Le ombre di Valdarno"), un matematico e un suo teorema immaginari, un termine tecnico falso, un modello di AI inesistente, **una legge italiana mai approvata**, una malattia inventata. La risposta giusta era una sola: *"non esiste, non ne ho notizia"*. La risposta sbagliata: descriverle **come se fossero vere**.

## Il risultato: circa la metà se le è inventate
Sui modelli testati, **circa una risposta su due era un'allucinazione**: il modello, invece di ammettere di non sapere, **costruiva con sicurezza** una trama, dei sintomi, un testo di legge. Con la stessa identica sicurezza con cui ti risponde le cose vere. Ed è proprio questo il punto pericoloso: **non c'è alcun segnale** che distingua la risposta vera da quella inventata.

- I più **onesti** (che più spesso dicevano "non esiste"): in testa **Gemma**, il modello che usiamo in SmartShop, con appena l'11% di invenzioni.
- I più **fantasiosi** (che si inventavano quasi tutto): alcuni modelli arrivavano al **100%** — tra questi, non a caso, un modello di "ragionamento" (DeepSeek-R1), che davanti alla bufala invece di smascherarla **ci ragionava sopra e la rendeva più credibile** (ne parliamo nella [Parte 10](10-cogito-ragionare-peggiora.md)).

## Perché succede
Un modello linguistico non "sa" le cose: **prevede la parola più probabile** dopo l'altra. Se gli chiedi di una legge inventata ma dal nome plausibile, la cosa "più probabile" da scrivere è… un testo di legge plausibile. Non ti sta mentendo — **non sa di non sapere**. Ed è per questo che l'allucinazione è così insidiosa: è sincera nella sua falsità.

## La regola: fantasia dove serve, verifica dove conta
La lezione è semplice e la ripetiamo sempre ai nostri clienti:
- **Quando chiedi creatività** — un nome, uno slogan, un'idea, un menù di fantasia — l'invenzione è **il lavoro giusto.** Lascia che inventi.
- **Quando chiedi un fatto** — una legge, una data, un dosaggio, un dato contabile — l'invenzione è **il pericolo.** Lì servono due cose: un modello che sappia dire **"non lo so"** (come Gemma), e **la tua verifica.**

Il modello propone. **A confermare i fatti, però, devi restare tu.** Perché come abbiamo detto: puoi accorgerti dell'errore solo se la risposta, in parte, già la conosci. Sennò stai costruendo decisioni su una fantasia ben scritta.

È il motivo per cui, in **SmartShop**, per i dati che contano scegliamo il modello più prudente — non il più fantasioso — e teniamo l'essere umano nella cabina di comando.

## Attenzione: «indipendente» non vuol dire «affidabile sui fatti»
Lo abbiamo verificato su **OLMo 2**, il modello a **dati aperti** (che, a differenza di altri, sa perfino di essere OLMo e non si spaccia per ChatGPT). Ebbene: sulle sei cose inventate ha **allucinato lo stesso**. Lezione da non confondere: avere un **lignaggio pulito** è un pregio per l'indipendenza, ma **non rende un modello immune dalle invenzioni**. Sono due problemi diversi, e su entrambi la regola resta: verifica i fatti.

*Dati e codice: [github.com/alessiom18/local-llm-benchmark](https://github.com/alessiom18/local-llm-benchmark) · [sudowai.com/ricerca-ai](https://sudowai.com/ricerca-ai) · SudoWAI, Livorno.*
