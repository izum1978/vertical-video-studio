import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
spec = importlib.util.spec_from_file_location("evalmod", ROOT / "training" / "eval_director.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def sb(total, types_):
    n = len(types_)
    seg = total / n
    return {"beats": [{"id": i + 1, "start": round(i * seg, 2), "end": round(total if i == n - 1 else (i + 1) * seg, 2),
                       "mode": "motion", "scene_type": t} for i, t in enumerate(types_)]}


def test_scoring():
    good = json.dumps(sb(20, ["window_stalker", "door_breach", "drag_void", "candle_paranoia"]))
    m = mod.score_one(good, 20.0)
    assert m["json_ok"] == m["schema_ok"] == m["whitelist_ok"] == m["no_repeat"] == m["coverage_ok"] == 1 and m["entropy"] == 2.0
    rep = mod.score_one(json.dumps(sb(20, ["window_stalker", "window_stalker", "drag_void", "candle_paranoia"])), 20.0)
    assert rep["no_repeat"] == 0 and rep["schema_ok"] == 0
    assert mod.score_one("мусор", 20.0)["json_ok"] == 0
    assert mod.score_one(json.dumps({"title": "x"}), 20.0)["schema_ok"] == 0
    wl = mod.score_one(json.dumps(sb(20, ["window_stalker", "zombie", "drag_void", "candle_paranoia"])), 20.0)
    assert wl["whitelist_ok"] == 0


def test_evaluate_aggregates():
    rows = [{"messages": [{"content": "s"}, {"content": "u"}], "meta": {"duration": 20.0}}] * 4
    outs = iter([json.dumps(sb(20, ["window_stalker", "door_breach", "drag_void", "candle_paranoia"]))] * 2 + ["мусор", "мусор"])
    r = mod.evaluate("m", rows, lambda *a: next(outs))
    assert r["json_ok"] == 0.5 and r["schema_ok"] == 0.5
