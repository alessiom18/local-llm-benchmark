#!/bin/bash
cd /home/alessio/llm_bench
for i in $(seq 1 360); do
  grep -q "MASTER FINITO" results/master.log 2>/dev/null && break
  sleep 30
done
echo "[$(date '+%T')] pipeline finita → genero grafici" >> results/finalize.log
/usr/bin/python3 make_charts.py >> results/finalize.log 2>&1
echo "[$(date '+%T')] grafici fatti" >> results/finalize.log
