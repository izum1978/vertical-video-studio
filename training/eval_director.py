"""Оценка режиссёра: сравнивает модели на отложенной выборке (director_val.jsonl).

  python training/eval_director.py --models qwen2.5:7b qwen2.5-director-v1 --limit 50

Метрики считаются теми же функциями, что и в бою (check_storyboard), плюс разнообразие.
"""
import argparse
import json
import sys
import time
from collections import Counter
from math import log2
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.director_llm import STORYBOARD_SCHEMA, call_ollama, check_storyboard, parse_json_loose  # noqa: E402
from app.scene_resolver import SCENE_RENDERERS, normalize_scene_type  # noqa: E402


def score_one(raw: str, total: float) -> dict:
    m = {"json_ok": 0, "schema_ok": 0, "whitelist_ok": 0, "no_repeat": 0, "coverage_ok": 0, "entropy": 0.0}
    try:
        sb = parse_json_loose(raw)
        m["json_ok"] = 1
    except Exception:  # noqa: BLE001
        return m
    beats = sb.get("beats") if isinstance(sb, dict) else None
    if not isinstance(beats, list) or not beats:
        return m
    errs = check_storyboard(sb, total)
    m["schema_ok"] = int(not errs)
    m["whitelist_ok"] = int(all(normalize_scene_type(b.get("scene_type")) for b in beats if b.get("mode") == "motion"))
    types = [normalize_scene_type(b.get("scene_type")) for b in beats]
    m["no_repeat"] = int(all(a != b for a, b in zip(types, types[1:])))
    m["coverage_ok"] = int(not any("дыра" in e or "заканчивается" in e for e in errs))
    c = Counter(t for t in types if t)
    n = sum(c.values()) or 1
    m["entropy"] = round(-sum(v / n * log2(v / n) for v in c.values()), 2)
    return m


def evaluate(model: str, rows: list[dict], caller) -> dict:
    agg, t0 = Counter(), time.time()
    for r in rows:
        system, user = r["messages"][0]["content"], r["messages"][1]["content"]
        total = float(r["meta"]["duration"])
        try:
            raw = caller(model, system, user)
        except Exception:  # noqa: BLE001
            raw = ""
        for k, v in score_one(raw, total).items():
            agg[k] += v
    n = max(1, len(rows))
    out = {k: round(v / n, 3) for k, v in agg.items()}
    out["sec_per_sample"] = round((time.time() - t0) / n, 1)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--val", default=str(ROOT / "training" / "data" / "director_val.jsonl"))
    ap.add_argument("--models", nargs="+", required=True)
    ap.add_argument("--limit", type=int, default=50)
    a = ap.parse_args()
    rows = [json.loads(l) for l in Path(a.val).read_text(encoding="utf-8").splitlines() if l.strip()][: a.limit]
    caller = lambda model, system, user: call_ollama(model, system, user, STORYBOARD_SCHEMA, 300)  # noqa: E731
    print(f"{'модель':32} json  схема whitelist без_повторов покрытие энтропия сек/пример")
    for m in a.models:
        r = evaluate(m, rows, caller)
        print(f"{m:32} {r['json_ok']:.2f}  {r['schema_ok']:.2f}  {r['whitelist_ok']:.2f}      {r['no_repeat']:.2f}"
              f"        {r['coverage_ok']:.2f}    {r['entropy']:.2f}     {r['sec_per_sample']}")


if __name__ == "__main__":
    main()
