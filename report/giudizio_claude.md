# Terzo giudice: valutazione esterna (Claude)

Oltre ai due giudici-modello locali (gemma4:31b e gemma4:12b), un terzo valutatore esterno (Claude) ha letto
le risposte reali su due task rappresentativi — **strategia commerciale** (ragionamento) e **code review** (tecnica)
— per tutti e 9 i modelli. Sintesi:

- **Vetta: Gemma4 12B alla pari di Gemma4 31B.** Diagnosi del problema, azioni concrete e contestuali, e (nel code
  review) individuazione della SQL injection con esempio d'attacco esplicito. Un modello da 12B che regge il 31B.
- **Forti:** Cogito 8B, Qwen3.6 35B, Qwen2.5-Coder 14B.
- **Medi:** Qwen2.5-Coder 32B, Llama-3.3 70B — corretti ma non eccezionali; **il 70B non giustifica il costo**.
- **Debole:** Qwen2.5 3B (confonde il tipo di attività, riferimenti anacronistici), DeepSeek-Coder 16B (sbaglia
  perfino il giorno richiesto).

**Accordo tra i tre giudici:** convergono sul cluster di testa (modelli piccoli/medi in cima) e sui fanalini di coda.
Diverge solo il "primo assoluto" — ed è una lezione in sé: **anche la scelta del giudice introduce un bias**; ciò che
resta robusto è che *nessun modello di frontiera domina e un modello contenuto compete con i giganti.*
