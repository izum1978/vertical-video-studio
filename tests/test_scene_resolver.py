import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "backend"))
from app.scene_resolver import normalize_scene_type, resolve_scene


def r(text="", **kw):
    beat = {"text": text, **kw}
    return resolve_scene(beat, kw.get("preset", "facts"), 0)


def test_director_choice_wins_over_keywords():
    # раньше «луч» в тексте перебивал выбор режиссёра
    assert resolve_scene({"scene_type": "door_breach", "text": "Это лучше, чем случай"}, "facts", 0) == ("door_breach", "scene_type")


def test_aliases():
    assert normalize_scene_type("creature") == "creature_turn"
    assert normalize_scene_type("Void") == "drag_void"
    assert normalize_scene_type("motion") is None
    assert normalize_scene_type("") is None


def test_false_positives_gone():
    for word, bad in [("начать", "chat_messenger"), ("случай", "corridor_flashlight"),
                      ("получилось", "corridor_flashlight"), ("лучше", "corridor_flashlight"),
                      ("столько", "candle_paranoia"), ("кодекс", "cyber_chip"),
                      ("шоколад", "kinetic_punch"), ("чипсы", "cyber_chip"),
                      ("правильно", "checklist_hud"), ("существует", "creature_turn"),
                      ("автомат", "atomic_orbit")]:
        name, reason = resolve_scene({"mode": "motion", "text": f"Нужно {word} сейчас"}, "facts", 0)
        assert name != bad or not reason.startswith("keyword"), (word, name, reason)


def test_true_positives():
    cases = {"Он смотрит в окно": "window_stalker", "луч фонаря дрожит": "corridor_flashlight",
             "за дверью тихо": "door_breach", "горит свеча": "candle_paranoia",
             "в глазок видно": "peephole_stalker", "под кроватью": "bedroom_peace",
             "ползёт по полу": "underbed_claws", "его двойник": "underbed_twin",
             "оно улыбнулось": "creature_turn", "и свет погас": "drag_void",
             "пришло сообщение": "chat_messenger", "новый чип": "cyber_chip",
             "атомный реактор": "atomic_orbit", "правило номер один": "checklist_hud"}
    for text, want in cases.items():
        got, reason = resolve_scene({"mode": "motion", "text": text}, "facts", 0)
        assert got == want, (text, got, reason)


def test_mode_chat_and_horror_rotation():
    assert resolve_scene({"mode": "chat", "text": "привет"}, "facts", 0)[0] == "chat_messenger"
    n0 = resolve_scene({"mode": "kinetic", "text": "тихо"}, "horror_rules", 0)
    n1 = resolve_scene({"mode": "kinetic", "text": "тихо"}, "horror_rules", 1)
    assert n0[1] == n1[1] == "horror_rotation" and n0[0] != n1[0]


def test_rotation_default():
    assert resolve_scene({"mode": "motion", "text": "ничего особенного"}, "facts", 0)[1] == "rotation"
