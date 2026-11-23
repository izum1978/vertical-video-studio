"""Тесты обучающей части художника сцен: компактный формат, датасет, оценка, критик композиции."""
import importlib.util
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
os.environ.setdefault("SCENE_CACHE_DIR", tempfile.mkdtemp(prefix="scene_cache_"))

from app.motion_gfx import designer as D  # noqa: E402
from app.motion_gfx.scene_dsl import normalize_spec, to_compact  # noqa: E402


def _load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "training" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


BS, ES = _load("build_scene_dataset"), _load("eval_scene")
GOOD = {"bg": {"preset": "indoor", "ground": "floor", "horizon": 0.5, "weather": "none"},
        "objects": [{"id": "t", "prop": "table", "x": 0.5, "y": 0.57, "scale": 1.7},
                    {"prop": "cup", "on": "t", "dx": -0.2, "scale": 1.0},
                    {"prop": "book", "on": "t", "dx": 0.2},
                    {"prop": "lamp", "x": 0.9, "y": 0.57, "lit": True, "anim": [{"type": "flicker", "amount": 0.2}]},
                    {"prop": "window", "x": 0.2, "y": 0.33, "layer": "back"}]}


def _llm(item):
    def f(provider, system, user, schema):
        if isinstance(item, Exception):
            raise item
        return (item if isinstance(item, str) else json.dumps(item, ensure_ascii=False)), "fake"
    return f


def test_compact_form_round_trips_for_offline_and_hand_written_scenes():
    texts = ["Взбиваем яйца и жарим омлет на сковороде.", "Ракета стартует на рассвете.", "Ночью сосед стоит у забора возле дома.",
             "Собака бежит по двору под дождём.", "Полёт к далёкой планете займёт семь лет."]
    specs = [normalize_spec(GOOD)[0]] + [normalize_spec(D.heuristic_scene(t, "facts"))[0] for t in texts]
    for spec in specs:
        compact = to_compact(spec)
        json.dumps(compact, ensure_ascii=False)
        again, _w = normalize_spec(compact)
        assert again is not None
        assert to_compact(again) == compact                 # формат устойчив: повторное сжатие ничего не меняет
        assert [o["prop"] for o in again["objects"]] == [o["prop"] for o in spec["objects"]]
        for a, b in zip(spec["objects"], again["objects"]):
            assert abs(a["x"] - b["x"]) < 0.01 and abs(a["y"] - b["y"]) < 0.01 and abs(a["scale"] - b["scale"]) < 0.01


def test_relevance_counts_props_named_in_the_text():
    spec = normalize_spec(GOOD)[0]
    assert D.relevance(spec, "Ставим чашку на стол у лампы") == 1.0
    assert D.relevance(spec, "Корабль плывёт мимо маяка") == 0.0
    assert D.relevance(spec, "Просто тишина") == 1.0          # в тексте предметов нет, придраться не к чему


def test_composition_critic_flags_real_problems():
    def spec_of(objs, ground="grass"):
        return normalize_spec({"bg": {"preset": "day", "ground": ground}, "objects": objs})[0]
    assert D.quality_errors(spec_of([{"prop": "tree", "x": 0.3, "y": 0.56}])) == ["слишком мало деталей: нужно 3-8"]
    stacked = spec_of([{"prop": "car", "x": 0.5, "y": 0.56}, {"prop": "house", "x": 0.5, "y": 0.56},
                       {"prop": "tree", "x": 0.52, "y": 0.56}])
    assert any("накладываются" in e or "в одном месте" in e for e in D.quality_errors(stacked))
    many = spec_of([{"prop": "tree", "x": i / 7, "y": 0.56} for i in range(6)])
    assert any("слишком много одинаковых" in e for e in D.quality_errors(many))
    tiny = spec_of([{"prop": "cup", "x": 0.2, "y": 0.56, "scale": 0.25}, {"prop": "cup", "x": 0.5, "y": 0.56, "scale": 0.25},
                    {"prop": "bottle", "x": 0.8, "y": 0.56, "scale": 0.25}])
    assert any("мелк" in e for e in D.quality_errors(tiny))
    space = normalize_spec({"bg": {"preset": "space", "ground": "none"},
                            "objects": [{"prop": "planet", "x": 0.7, "y": 0.3}, {"prop": "star", "x": 0.2, "y": 0.2},
                                        {"prop": "rocket", "x": 0.4, "y": 0.5, "scale": 1.4}]})[0]
    assert "нет ни одной детали на земле" not in D.quality_errors(space)       # в космосе земли нет


def test_offline_designer_output_always_passes_the_critic():
    for t in ["Взбиваем яйца и жарим омлет.", "Ночью в доме погас свет, сосед стоит у забора.", "Кошка спит на кровати, рядом лампа и книга.",
              "Машина едет по дороге мимо большого дома.", "Маяк светит над морем, лодка плывёт к берегу.", "Полёт к планете займёт семь лет."]:
        spec = normalize_spec(D.heuristic_scene(t, "facts"))[0]
        assert D.quality_errors(spec) == [], t


def test_dataset_record_matches_runtime_prompt_and_is_canonical():
    text = "Ставим чашку на стол у лампы."
    rec, why = BS.build_record("facts", text, _llm(GOOD), provider="claude")
    assert rec and why is None
    system, user, assistant = [m["content"] for m in rec["messages"]]
    assert system == D.system_prompt()
    assert user == D.build_user_prompt(text, "", {"title": text[:40], "preset": "facts", "provider": "claude", "prev": ""})
    assert normalize_spec(json.loads(assistant), "facts")[0] is not None
    assert rec["meta"]["split"] in ("train", "val") and rec["meta"]["relevance"] == 1.0


def test_dataset_rejects_bad_scenes_with_reasons():
    rec, why = BS.build_record("facts", "Корабль плывёт мимо маяка.", _llm(GOOD))
    assert rec is None and "смысл" in why                                 # в сцене нет ни корабля, ни маяка
    rec, why = BS.build_record("facts", "Ставим чашку на стол.", _llm(ConnectionError("нет сети")))
    assert rec is None and "LLM" in why                                   # словарь в датасет не берём
    few = {"bg": {"preset": "indoor"}, "objects": [{"prop": "cup", "x": 0.3, "y": 0.55}, {"prop": "table", "x": 0.6, "y": 0.57}]}
    rec, why = BS.build_record("facts", "Чашка на столе.", _llm(few))
    assert rec is None
    assert BS.split_of("а") == BS.split_of("а")
    assert 100 < sum(BS.split_of(f"фраза {i}") == "val" for i in range(1500)) < 200


def test_starter_sentence_file_is_usable():
    lines = [l for l in (ROOT / "training" / "scene_sentences.txt").read_text(encoding="utf-8").splitlines() if "|" in l and not l.startswith("#")]
    pairs = [l.split("|", 1) for l in lines]
    assert len(pairs) >= 80 and len({t for _p, t in pairs}) == len(pairs)
    assert {p for p, _t in pairs} <= {"facts", "horror_rules", "story"}


def test_eval_scoring_of_model_answers():
    good = ES.score_one(json.dumps(GOOD), "Ставим чашку на стол у лампы", "facts")
    assert good["json_ok"] == good["spec_ok"] == good["quality_ok"] == 1 and good["relevance"] == 1.0 and good["unknown_props"] == 0.0
    assert ES.score_one("мусор", "т", "facts")["json_ok"] == 0
    wrong = dict(GOOD, objects=GOOD["objects"] + [{"prop": "динозавр", "x": 0.4, "y": 0.5}])
    assert abs(ES.score_one(json.dumps(wrong), "т", "facts")["unknown_props"] - 1 / 6) < 1e-9
    rows = [{"messages": [{"content": "s"}, {"content": "u"}], "meta": {"text": "Ставим чашку на стол у лампы", "preset": "facts"}}] * 4
    seq = iter([json.dumps(GOOD)] * 2 + ["мусор"] * 2)
    r = ES.evaluate("m", rows, lambda *a: next(seq))
    assert r["json_ok"] == 0.5 and r["quality_ok"] == 0.5
