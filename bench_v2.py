#!/usr/bin/env python3
"""Benchmark v2 — num_predict raddoppiati per evitare troncamento."""
import json, sys, time, os, requests
from tasks_realworld import REAL_TASKS, CODE_WITH_BUG

OLLAMA = os.getenv('OLLAMA_URL', 'http://localhost:11434')

# Raddoppia num_predict per ogni task
TASK_V2 = []
for t in REAL_TASKS:
    t2 = dict(t)
    t2['np'] = min(t['np'] * 4, 4000)  # max 4000 — serve per task lunghi
    TASK_V2.append(t2)

def get_models():
    r = requests.get(f'{OLLAMA}/api/tags')
    return [m['name'] for m in r.json()['models']]

def run_task(model, task):
    t0 = time.time()
    try:
        r = requests.post(f'{OLLAMA}/api/chat', json={
            'model': model,
            'messages': [
                {'role': 'system', 'content': task['sys']},
                {'role': 'user', 'content': task['prompt']}
            ],
            'stream': False,
            'options': {
                'temperature': 0.3,
                'num_predict': task['np']
            }
        }, timeout=300)
        elapsed = time.time() - t0
        resp = r.json()['message']['content']
        tokens = r.json().get('eval_count', 0)
        return {'response': resp, 'tokens': tokens, 'time': round(elapsed, 1), 'error': None}
    except Exception as e:
        return {'response': '', 'tokens': 0, 'time': 0, 'error': str(e)}

def main():
    models = sys.argv[1:] if len(sys.argv) > 1 else get_models()
    # salta modelli > 30GB (swap troppo lento)
    skip = ['qwen3.6:35b', 'hf.co/*', 'qwen2.5:32b', 'qwen3.5:32b']
    
    outfile = f'/home/alessio/llm_bench/results/bench_v2_{time.strftime("%Y%m%d_%H%M")}.jsonl'
    total = len(models) * len(TASK_V2)
    done = 0
    
    for model in models:
        skip_model = False
        for s in skip:
            if s.startswith('hf.co') and 'hf.co' in model:
                skip_model = True
            elif model == s:
                skip_model = True
        if skip_model:
            done += len(TASK_V2)
            continue
            
        for task in TASK_V2:
            done += 1
            print(f'[{done}/{total}] {model:<50} {task["id"]:<22}', end=' ', flush=True)
            result = run_task(model, task)
            if result['error']:
                print(f'❌ {result["error"][:60]}')
            else:
                trunc = '⚠️' if not result['response'].rstrip().endswith(('.', '!', '?', '>', '`', '}', ']')) else '✅'
                print(f'[{result["tokens"]:>4}tok {result["time"]:>5.1f}s] {trunc}')
            
            record = {
                'model': model,
                'task': task['id'],
                'category': task['cat'],
                'prompt': task['prompt'][:200],
                'response': result['response'],
                'tokens': result['tokens'],
                'time': result['time'],
                'error': result['error'],
                'num_predict': task['np'],
                'ok': not result['error'],
                'ts': time.strftime('%Y-%m-%dT%H:%M:%S')
            }
            with open(outfile, 'a') as f:
                f.write(json.dumps(record, ensure_ascii=False) + '\n')
                f.flush()
    
    print(f'\n✅ Completato: {outfile}')

if __name__ == '__main__':
    main()
