import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
spec = importlib.util.spec_from_file_location("builder", ROOT / "training" / "build_director_dataset.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

SCRIPT = ("Если ночью пропадёт связь, не выходи из дома. Правило первое: потуши свет и отойди от окон. "
          "Правило второе: заблокируй лестницу. Правило третье: не отвечай на голос из коридора. "
          "Что дальше, расскажу в следующей части.")


def script_fn(topic, preset):
    return {"script": SCRIPT, "title": topic}


def timing_fn(s):
    return mod.estimate_timing(s)


def sb(total, types=None, shots=True, n=6):
    types = types or ["window_stalker", "peephole_stalker", "door_breach", "corridor_flashlight", "candle_paranoia", "drag_void"]
    seg = total / n
    beats = []
    for i in range(n):
        b = {"id": i + 1, "start": round(i * seg, 2), "end": round(total if i == n - 1 else (i + 1) * seg, 2),
             "text": "т", "mode": "motion", "scene_type": types[i % len(types)], "title": "ТИТУЛ", "subtitle": "ПОДПИСЬ"}
        if shots:
            b["camera_shot"], b["camera_motion"] = "wide", "zoom_in"
        beats.append(b)
    return {"beats": beats}


def test_good_record_is_canonical_and_matches_runtime_prompt():
    _, total = timing_fn(SCRIPT)
    rec, why = mod.build_record("Тема А", "horror_rules", script_fn, timing_fn, lambda s, u: json.dumps(sb(total)))
    assert rec and why is None
    system, user, assistant = [m["content"] for m in rec["messages"]]
    assert system == mod.DIRECTOR_SYSTEM_PROMPT
    assert "Предложения с таймкодами:" in user and "S5 [" in user
    data = json.loads(assistant)
    assert list(data) == ["beats"] and data["beats"][0]["start"] == 0.0 and data["beats"][-1]["end"] == total
    assert all(set(b) == set(mod.BEAT_FIELDS) for b in data["beats"])
    assert rec["meta"]["split"] in ("train", "val")


def test_bad_quality_is_rejected_after_retries():
    _, total = timing_fn(SCRIPT)
    calls = []

    def llm(s, u):
        calls.append(u)
        return json.dumps(sb(total, shots=False))   # нет camera_* -> отбраковка

    rec, why = mod.build_record("Тема Б", "horror_rules", script_fn, timing_fn, llm)
    assert rec is None and "camera_shot" in why and len(calls) == 3
    assert "не подошёл" in calls[1]


def test_retry_recovers():
    _, total = timing_fn(SCRIPT)
    seq = ["не json вообще", json.dumps(sb(total))]
    rec, why = mod.build_record("Тема В", "horror_rules", script_fn, timing_fn, lambda s, u: seq.pop(0))
    assert rec is not None


def test_horror_needs_horror_scenes():
    _, total = timing_fn(SCRIPT)
    bad = sb(total, types=["cyber_chip", "atomic_orbit", "dynamic_canvas", "kinetic_punch", "checklist_hud", "chat_messenger"])
    rec, why = mod.build_record("Тема Г", "horror_rules", script_fn, timing_fn, lambda s, u: json.dumps(bad))
    assert rec is None and "не хоррор-сцена" in why


def test_split_is_stable_and_roughly_10_percent():
    assert mod.split_of("abc") == mod.split_of("abc")
    val = sum(mod.split_of(f"тема {i}") == "val" for i in range(2000))
    assert 140 < val < 260, val
