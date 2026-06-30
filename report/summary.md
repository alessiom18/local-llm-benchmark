# Risultati benchmark — *non esiste il modello migliore*

Fonte: `results_20260630_0104.jsonl` · 115 test validi

## Classifica per qualità media (check automatici, 0–1)

| # | Modello | Tier | Qualità | Pass | Velocità (tok/s) | Test |
|---|---------|------|---------|------|------------------|------|
| 1 | Qwen2.5 3B (default) | light | **1.0** | 100% | 115.62 | 13 |
| 2 | Cogito 8B | light | **1.0** | 100% | 61.621 | 13 |
| 3 | Qwen2.5-Coder 32B abliterated | heavy | **1.0** | 100% | 3.182 | 13 |
| 4 | Llama-3.3 70B abliterated | heavy | **1.0** | 100% | 1.029 | 11 |
| 5 | Qwen2.5-Coder 14B | light | **0.987** | 100% | 21.804 | 13 |
| 6 | DeepSeek-Coder-V2 16B | light | **0.948** | 92% | 73.25 | 13 |
| 7 | Gemma4 12B | light | **0.93** | 77% | 35.399 | 13 |
| 8 | Qwen3.6 35B (MoE) | heavy | **0.911** | 77% | 30.898 | 13 |
| 9 | Gemma4 31B | heavy | **0.881** | 77% | 2.665 | 13 |

## Qualità per categoria (chi vince dove)

| Modello | classify | code | config | copy | extract | recipe | strategy | website |
|---|---|---|---|---|---|---|---|---|
| Qwen2.5 3B (default) | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| Cogito 8B | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| Qwen2.5-Coder 32B abliterated | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| Llama-3.3 70B abliterated | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 0 |
| Qwen2.5-Coder 14B | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 0.915 |
| DeepSeek-Coder-V2 16B | 0.665 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| Gemma4 12B | 1.0 | 1.0 | 1.0 | 0.43 | 1.0 | 1.0 | 1.0 | 0.83 |
| Qwen3.6 35B (MoE) | 1.0 | 0.835 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 0.585 |
| Gemma4 31B | 1.0 | 1.0 | 1.0 | 0.45 | 1.0 | 1.0 | 1.0 | 0.5 |

> Tesi: nessun modello domina ovunque; un setup contenuto e ben instradato batte i giganti su molti task reali.