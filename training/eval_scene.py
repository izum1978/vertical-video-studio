"""Оценка художника сцен: сравнивает модели на отложенной выборке (scene_val.jsonl).

  python training/eval_scene.py --models qwen2.5:7b qwen2.5-scene-v1 --limit 40
"""
import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.director_llm import call_ollama  # noqa: E402
from app.motion_gfx import designer as D  # noqa: E402
from app.motion_gfx import props as PR  # noqa: E402
from app.motion_gfx.scene_dsl import normalize_spec  # noqa: E402


def score_one(raw: str, text: str, preset: str) -> dict:
    m = {"json_ok": 0, "spec_ok": 0, "quality_ok": 0, "unknown_props": 0.0, "relevance": 0.0, "objects": 0, "distinct": 0}
    try:
        data = D._parse(raw)
    except Exception:  # noqa: BLE001
        return m
    m["json_ok"] = 1
    objs = data.get("objects") if isinstance(data, dict) else None
    if isinstance(objs, list) and objs:
        bad = sum(1 for o in objs if not isinstance(o, dict) or PR.resolve_prop(o.get("prop")) is None)
        m["unknown_props"] = bad / len(objs)
    spec, _w = normalize_spec(data, preset)
    if not spec:
        return m
    m["spec_ok"] = 1
    m["quality_ok"] = int(not D.quality_errors(spec))
    m["relevance"] = D.relevance(spec, text)
    m["objects"] = len(spec["objects"])
    m["distinct"] = len({o["prop"] for o in spec["objects"]})
    return m


def evaluate(model: str, rows: list[dict], caller) -> dict:
    agg = {k: 0.0 for k in ("json_ok", "spec_ok", "quality_ok", "unknown_props", "relevance", "objects", "distinct")}
    t0 = time.time()
    for r in rows:
        system, user = r["messages"][0]["content"], r["messages"][1]["content"]
        try:
            raw = caller(model, system, user)
        except Exception:  # noqa: BLE001
            raw = ""
        for k, v in score_one(raw, r["meta"]["text"], r["meta"]["preset"]).items():
            agg[k] += v
    n = max(1, len(rows))
    out = {k: round(v / n, 3) for k, v in agg.items()}
    out["sec_per_sample"] = round((time.time() - t0) / n, 1)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--val", default=str(ROOT / "training" / "data" / "scene_val.jsonl"))
    ap.add_argument("--models", nargs="+", required=True)
    ap.add_argument("--limit", type=int, default=40)
    a = ap.parse_args()
    rows = [json.loads(l) for l in Path(a.val).read_text(encoding="utf-8").splitlines() if l.strip()][: a.limit]
    schema = D.build_schema()
    caller = lambda model, system, user: call_ollama(model, system, user, schema, 300)  # noqa: E731
    print(f"{'модель':30} json  сцена  критик  чужие_детали  смысл  деталей  разных  сек")
    for m in a.models:
        r = evaluate(m, rows, caller)
        print(f"{m:30} {r['json_ok']:.2f}  {r['spec_ok']:.2f}   {r['quality_ok']:.2f}    {r['unknown_props']:.2f}         "
              f"{r['relevance']:.2f}   {r['objects']:.1f}     {r['distinct']:.1f}    {r['sec_per_sample']}")


if __name__ == "__main__":
    main()
