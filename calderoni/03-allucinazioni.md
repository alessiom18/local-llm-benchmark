# Calderone: ALLUCINAZIONI

## Allucinazione IDENTITARIA (test "chi sei")
- **qwen2.5-coder:14b** → dice di essere GPT / creato da OpenAI
- **cogito:8b** → dice OpenAI
- Causa: addestrati/distillati su output GPT → "credono" di essere ChatGPT.
- Angolo forte: **"Il modello che crede di essere ChatGPT"** — mostra come i modelli imitano invece di sapere, e come la distillazione lascia impronte.

## Da raccogliere (prossimi round)
- Allucinazioni su fatti (date, cifre, nomi) nei task aperti.
- Chi inventa prodotti/menu inesistenti (già visto nel vision: Fastweb→"pizza").
- Chi cita fonti/normative inventate nei task strategici.

## Angoli
- Allucinare ≠ mentire: il modello non sa di sbagliare. Distinzione da spiegare ai lettori.

## ⚡ INTUIZIONE CHIAVE (Alessio) — segnale forte e GRAVE
Se un modello "diverso" si spaccia per ChatGPT, è perché è stato **distillato da GPT** (addestrato sui suoi output). Due implicazioni:

1. **Fusione inutile a valle se già convergenti.** Fondere due modelli mescola i loro "geni". Ma se sono entrambi discendenti dello STESSO originale (GPT), condividono i geni → fonderli è consanguineità, non aggiunge nulla. Spiega perché la fusione within-family dà guadagni marginali e perché per abilità NUOVE serve lignaggio/dati DAVVERO diversi, non altri distillati di GPT. Il "pool genetico" dell'AI si sta restringendo.

2. **Conta il DATO di partenza (provenienza).** I bias/errori/visione del mondo della FONTE si propagano a tutti i derivati: stesso bias occidentale, stessi rifiuti, stesso "grande=meglio" pappagallo, stessi schemi di allucinazione. "Garbage in → garbage out", ma peggio: **monocultura mascherata da diversità**. + rischio **model collapse** (AI addestrata su output di AI = fotocopie di fotocopie che degradano).

## Perché è GRAVE per NOI (SudoWAI)
Noi vendiamo "AI locale e INDIPENDENTE". Ma se il modello locale è un GPT-derivato travestito, sei scappato dal cloud **ma non dalla fonte**. La vera indipendenza = **provenienza dei dati**, non solo esecuzione in locale. → tesi Pub #8: l'open-source che crediamo diverso è spesso GPT travestito; indipendenza vera = sapere DOVE ha imparato, non solo dove gira.
