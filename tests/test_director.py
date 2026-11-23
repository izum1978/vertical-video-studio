import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app import director, director_llm as D

SCRIPT = ("Если ночью пропадёт связь, не выходи из дома. Правило первое: потуши свет и отойди от окон. "
          "Правило второе: заблокируй лестницу. Правило третье: не отвечай на голос из коридора. "
          "Что делать дальше, расскажу в следующей части.")
WORDS = []
t = 0.0
for w in D.clean_for_tts(SCRIPT).split():
    WORDS.append({"word": w, "start": round(t, 2), "end": round(t + 0.4, 2)})
    t += 0.42
TOTAL = round(t + 0.3, 2)


def good_sb(total):
    k = 5
    seg = total / k
    types = ["window_stalker", "peephole_stalker", "door_breach", "corridor_flashlight", "drag_void"]
    return {"beats": [{"id": i + 1, "start": round(i * seg, 2), "end": round(total if i == k - 1 else (i + 1) * seg, 2),
                       "text": "x", "mode": "motion", "scene_type": types[i], "title": "ТИТУЛ", "subtitle": "ПОДПИСЬ"} for i in range(k)]}


def run(llm, **kw):
    logs = []
    sb = director.direct_storyboard({"script": SCRIPT, "title": "Тест"}, WORDS, TOTAL, preset="horror_rules",
                                    provider_name="qwen", log=logs.append, **kw) if llm is None else \
         D.direct_storyboard_v2({"script": SCRIPT, "title": "Тест"}, WORDS, TOTAL, preset="horror_rules",
                                provider_name="qwen", log=logs.append, llm=llm,
                                fallback=director.create_fallback_storyboard, repair=director.validate_and_repair_storyboard)
    return sb, logs


def test_sentences_cover_whole_audio_without_gaps():
    s = D.split_sentences_with_timing(SCRIPT, WORDS, TOTAL)
    assert len(s) == 5 and s[0]["start"] == 0.0 and s[-1]["end"] == TOTAL
    assert all(a["end"] == b["start"] for a, b in zip(s, s[1:]))
    assert all(x["end"] > x["start"] for x in s)


def test_sentences_without_timestamps():
    s = D.split_sentences_with_timing(SCRIPT, None, 20.0)
    assert s[0]["start"] == 0.0 and s[-1]["end"] == 20.0 and len(s) == 5


def test_prompt_contains_every_sentence():
    s = D.split_sentences_with_timing(SCRIPT, WORDS, TOTAL)
    p = D.build_user_prompt("Тест", "horror_rules", TOTAL, s)
    assert "S5 [" in p and "следующей части" in p


def test_retry_with_feedback_then_success():
    calls = []

    def llm(provider, system, user, schema):
        calls.append(user)
        return (json.dumps({"title": "a"}) if len(calls) == 1 else json.dumps(good_sb(TOTAL))), "qwen-test"

    sb, logs = run(llm)
    info = sb["meta"]["director"]
    assert info["source"] == "qwen" and info["attempts"] == 2 and info["model"] == "qwen-test"
    assert "содержал ошибки" in calls[1] and "нет непустого массива beats" in calls[1]
    assert sb["beats"][-1]["end"] == TOTAL


def test_unknown_scene_type_is_flagged_and_retried():
    bad = good_sb(TOTAL)
    bad["beats"][2]["scene_type"] = "zombie_party"
    seq = [json.dumps(bad), json.dumps(good_sb(TOTAL))]
    sb, _ = run(lambda *a: (seq.pop(0), "m"))
    assert sb["meta"]["director"]["attempts"] == 2
    assert all(b["scene_type"] for b in sb["beats"])


def test_always_failing_llm_gives_fallback_with_reasons():
    def llm(*a):
        raise ConnectionError("Ollama недоступна")
    sb, logs = run(llm)
    info = sb["meta"]["director"]
    assert info["source"] == "fallback" and info["attempts"] == 2
    assert any("Ollama недоступна" in e for e in info["errors"])
    assert any("шаблон" in l for l in logs)
    assert sb["beats"][-1]["end"] == TOTAL


def test_json_inside_chatter_is_parsed():
    raw = "Конечно! Вот раскадровка:\n```json\n" + json.dumps(good_sb(TOTAL)) + "\n```"
    sb, _ = run(lambda *a: (raw, "m"))
    assert sb["meta"]["director"]["source"] == "qwen" and sb["meta"]["director"]["attempts"] == 1


def test_validator_whitelists_scene_type_and_keeps_camera():
    sb = {"beats": [{"id": 1, "start": 0, "end": 3, "mode": "motion", "scene_type": "creature", "text": "t",
                     "camera_shot": "wide", "camera_motion": "zoom_in"},
                    {"id": 2, "start": 3, "end": 6, "mode": "motion", "scene_type": "nonsense", "text": "t"}]}
    ok, msg, rep = director.validate_and_repair_storyboard(sb, 6.0)
    assert ok and rep["beats"][0]["scene_type"] == "creature_turn" and rep["beats"][0]["camera_shot"] == "wide"
    assert rep["beats"][1]["scene_type"] == ""   # пусто -> решит resolve_scene по ключевым словам


def test_mock_mode_and_providers():
    sb = director.direct_storyboard({"script": SCRIPT, "title": "t"}, None, 12.0, preset="facts", mock=True)
    assert sb["meta"]["director"]["source"] == "mock"
    for p in ("qwen", "qwen_local", "gemini", "openai", "claude", "anthropic"):
        D._models_for(p)
    try:
        D._models_for("nope")
        assert False
    except ValueError:
        pass
