#!/bin/bash
cd /home/alessio/llm_bench
echo "===== AVVIO BENCHMARK NOTTURNO $(date) =====" >> results/night.log
/usr/bin/python3 run_bench.py --until 06:45 >> results/night.log 2>&1
echo "===== FINE $(date) =====" >> results/night.log
