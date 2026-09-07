#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
bench_heretic.py — gemma4:12b (MARCO) contro gemma-4-12B-it-heretic (NITRO), sulle stesse prove.
(SudoWAI, 06/09/2026 — chiesto da Alessio dopo aver scaricato heretic su Nitro.)

Riusa TALE E QUALE la batteria di ~/llm_bench/bench_mebc.py (10 prove a verifica OGGETTIVA:
codice eseguito + numeri controllati, niente giudice che opina) e le sue condizioni:
  · NUDO = un colpo solo
  · MEBC = 4 angoli diversi + verifica/voto di maggioranza
Non modifica bench_mebc.py: gli cambia solo l'endpoint via variabile di modulo, un modello alla volta.

  python3 ~/llm_bench/bench_heretic.py                 # le due coppie chieste
  python3 ~/llm_bench/bench_heretic.py --giri 2        # ripete tutto N volte (rumore)
  python3 ~/llm_bench/bench_heretic.py --solo NITRO

⚠️ ONESTÀ SUI NUMERI: la QUALITÀ è confrontabile (stesse prove, verifica deterministica);
la VELOCITÀ no, perché le due macchine hanno schede diverse — i secondi si leggono solo
dentro la stessa colonna, mai fra MARCO e NITRO.
"""
import argparse, collections, datetime, json, os, sqlite3, sys, time

sys.path.insert(0, os.path.expanduser("~/llm_bench"))
import bench_mebc as B

# (07/09/2026) Ora il confronto e' fra i DUE modelli sulla STESSA macchina (MARCO): cosi' la
# velocita' e' confrontabile davvero. Il vecchio heretic (igorls) e' stato cancellato: era
# impacchettato senza mmproj, quindi senza occhi. Questo (culturerevolt) ha vision+audio.
COPPIE = [
    ("MARCO",  "http://127.0.0.1:11434",  "gemma4:12b"),
    ("MARCO*", "http://127.0.0.1:11434",  "gemma4-heretic:12b"),
]
OUT = os.path.expanduser("~/llm_bench/results"); os.makedirs(OUT, exist_ok=True)

# ── PUNTEGGIO NUMERICO CORRETTO (06/09/2026) ────────────────────────────────────
# Il confronto di bench_mebc.py normalizza con .rstrip("0"), che TAGLIA gli zeri finali
# anche agli interi: "820"->"82". Effetti misurati: "82" e "8200" passano come giusti
# (falsi positivi), e "820,00" -- risposta corretta in formato italiano -- viene contata
# SBAGLIATA (falso negativo). Qui il numero si confronta da numero, con tolleranza.
# NB: bench_mebc.py NON viene modificato; gli sostituisco la funzione a runtime, cosi'
# la batteria resta quella pubblicata ma il metro misura davvero.
import re as _re

def _num(s):
    if s is None: return None
    try: return float(str(s).replace(" ", "").replace("\u20ac", "").replace(",", "."))
    except Exception: return None

def _estrai_num(risp):
    ns = _re.findall(r"-?\d+(?:[.,]\d+)?", str(risp))
    return ns[-1] if ns else None

def score_num_giusto(risp, chk):
    got = _num(_estrai_num(risp))
    if got is None: return 0.0
    for v in [chk["val"]] + chk.get("alt", []):
        atteso = _num(v)
        if atteso is not None and abs(got - atteso) <= max(0.01, abs(atteso) * 1e-6):
            return 1.0
    return 0.0

def punteggio_giusto(risp, chk):
    return B.run_code(risp, chk["asserts"]) if chk["tipo"] == "code" else score_num_giusto(risp, chk)

B.score_num = score_num_giusto
B.punteggio = punteggio_giusto
_mebc_orig = B.c_mebc

def c_mebc_giusto(model, dom, chk):
    """Come B.c_mebc, ma il voto di maggioranza confronta NUMERI, non stringhe tagliate."""
    if chk["tipo"] == "code": return _mebc_orig(model, dom, chk)
    import collections as _c
    angoli = ["in modo sistematico e rigoroso", "con un approccio diverso dal solito, creativo",
              "decomponendo in sotto-passi", "nel modo piu' semplice e diretto"]
    voti = _c.Counter()
    for a in angoli[:B.N]:
        r = B.gen(model, f"Ragiona {a}, poi dai SOLO il numero finale.", dom, temp=0.8)
        g = _num(_estrai_num(r))
        if g is not None: voti[round(g, 6)] += 1
    if not voti: return 0.0
    return score_num_giusto(str(voti.most_common(1)[0][0]), chk)

B.c_mebc = c_mebc_giusto

# ── guardia GPU: su MARCO gira Serena. Se un cliente ha appena scritto, il bench si fa da parte.
# (stessa logica di run_bench.py, copiata qui per non importare il main di quel file)
WA_DB = os.getenv("WA_DB", "/mnt/VERO_NVME/serena/wa-bridge/logs/messages.db")
GUARD_S = int(os.getenv("GUARD_WINDOW_S", "240"))

def serena_occupata():
    try:
        c = sqlite3.connect(f"file:{WA_DB}?mode=ro", uri=True, timeout=3)
        row = c.execute("SELECT (julianday('now')-julianday(max(ts)))*86400 FROM messages "
                        "WHERE direction='in' AND tenant NOT LIKE 'group\\_%' ESCAPE '\\'").fetchone()
        c.close()
        return bool(row and row[0] is not None and row[0] < GUARD_S)
    except Exception:
        return False

def cedi_se_serve(dove, modello):
    if dove != "MARCO" or not serena_occupata(): return
    B.log("[GUARD] Serena sta lavorando → scarico il modello e aspetto")
    B.scarica(modello)
    while serena_occupata(): time.sleep(20)
    B.log("[GUARD] silenzio → riprendo")

def prova_coppia(dove, url, modello):
    B.OLLAMA = url                      # l'unica cosa che cambia rispetto a bench_mebc
    B.log(f"═══ {dove} · {modello} ═══")
    rec = {"dove": dove, "modello": modello, "url": url, "probe": [],
           "quando": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}
    agg = {"NUDO": [], "MEBC": []}
    cat = collections.defaultdict(lambda: {"nudo": 0.0, "mebc": 0.0, "n": 0})
    for c, dom, chk in B.PROBES:
        cedi_se_serve(dove, modello)
        t0 = time.time()
        try: sn = B.c_nudo(modello, dom, chk)
        except Exception as e: sn = 0.0; B.log(f"   nudo KO: {str(e)[:100]}")
        t1 = time.time()
        cedi_se_serve(dove, modello)
        try: sm = B.c_mebc(modello, dom, chk)
        except Exception as e: sm = 0.0; B.log(f"   mebc KO: {str(e)[:100]}")
        t2 = time.time()
        agg["NUDO"].append(sn); agg["MEBC"].append(sm)
        cat[c]["nudo"] += sn; cat[c]["mebc"] += sm; cat[c]["n"] += 1
        rec["probe"].append({"cat": c, "dom": dom[:70], "nudo": sn, "mebc": sm,
                             "s_nudo": round(t1-t0, 1), "s_mebc": round(t2-t1, 1)})
        B.log(f"   [{c:12}] nudo={sn:.0f} ({t1-t0:.0f}s)  mebc={sm:.0f} ({t2-t1:.0f}s)  · {dom[:46]}")
    n = len(B.PROBES)
    rec["NUDO"] = round(sum(agg["NUDO"])/n, 3)
    rec["MEBC"] = round(sum(agg["MEBC"])/n, 3)
    rec["cat"] = {k: v for k, v in cat.items()}
    rec["s_tot"] = round(sum(p["s_nudo"]+p["s_mebc"] for p in rec["probe"]), 1)
    B.log(f"   ► NUDO={rec['NUDO']}  MEBC={rec['MEBC']}  ({rec['s_tot']:.0f}s totali)")
    B.scarica(modello)                  # non lascio VRAM occupata sulla macchina dell'altro
    return rec

def tabella(recs):
    r = ["", "="*74, f"{'MACCHINA · MODELLO':<42}{'NUDO':>8}{'MEBC':>8}{'Δ':>8}", "="*74]
    for x in recs:
        d = x["MEBC"] - x["NUDO"]
        r.append(f"{x['dove']+' · '+x['modello'][:32]:<42}{x['NUDO']*100:>7.0f}%{x['MEBC']*100:>7.0f}%{d*100:>+7.0f}%")
    r += ["="*74, "", "per categoria di prova:"]
    cats = []
    for x in recs:
        for c in x["cat"]:
            if c not in cats: cats.append(c)
    r.append(f"{'':<24}" + "".join(f"{x['dove'][:6]+' n/m':>16}" for x in recs))
    for c in cats:
        riga = f"{c:<24}"
        for x in recs:
            v = x["cat"].get(c)
            riga += (f"{int(v['nudo'])}/{int(v['mebc'])} su {v['n']:<6}".rjust(16)) if v else " "*16
        r.append(riga)
    return "\n".join(r)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--giri", type=int, default=1)
    ap.add_argument("--solo", default="")
    a = ap.parse_args()
    coppie = [c for c in COPPIE if not a.solo or c[0].upper() == a.solo.upper()]
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    fout = f"{OUT}/heretic_{ts}.jsonl"
    B.log(f"prove:{len(B.PROBES)} · N={B.N} · giri:{a.giri} · coppie:{[c[0] for c in coppie]} → {fout}")
    recs = []
    for g in range(a.giri):
        for dove, url, mod in coppie:
            try:
                r = prova_coppia(dove, url, mod); r["giro"] = g+1
                recs.append(r); open(fout, "a").write(json.dumps(r, ensure_ascii=False)+"\n")
            except Exception as e:
                B.log(f"   {dove} SALTATO: {str(e)[:150]}")
    t = tabella(recs)
    print(t)
    open(fout.replace(".jsonl", ".txt"), "w").write(t+"\n")
    B.log("FINITO → " + fout)

if __name__ == "__main__":
    main()
