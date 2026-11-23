"""Тесты генерации сцен: детали, описание сцены, рендер, художник (LLM и словарь), политика, интеграция."""
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
os.environ["SCENE_CACHE_DIR"] = tempfile.mkdtemp(prefix="scene_cache_")

from app import director_llm as DL  # noqa: E402
from app.motion_gfx import designer as D  # noqa: E402
from app.motion_gfx import plan_storyboard, render_plan  # noqa: E402
from app.motion_gfx import props as PR  # noqa: E402
from app.motion_gfx import scene_dsl as DSL  # noqa: E402
from app.motion_gfx.engine import draw_frame  # noqa: E402
from app.motion_gfx.lexicon import find_props  # noqa: E402

GOOD = {"bg": {"preset": "indoor", "ground": "floor", "horizon": 0.5, "weather": "none"},
        "objects": [{"id": "t", "prop": "table", "x": 0.5, "y": 0.57, "scale": 1.7},
                    {"prop": "pan", "on": "t", "dx": -0.05, "lit": True},
                    {"prop": "cup", "on": "t", "dx": 0.25},
                    {"prop": "lamp", "x": 0.9, "y": 0.57, "lit": True}]}


def _llm(*specs, calls=None):
    seq = list(specs)

    def llm(provider, system, user, schema):
        if calls is not None:
            calls.append(user)
        item = seq.pop(0) if len(seq) > 1 else seq[0]
        if isinstance(item, Exception):
            raise item
        return (item if isinstance(item, str) else json.dumps(item, ensure_ascii=False)), "fake-model"
    return llm


def test_every_prop_renders_and_dynamic_props_change_over_time():
    assert len(PR.REGISTRY) >= 50
    for name, pr in PR.REGISTRY.items():
        for scale in (0.2, 0.5):
            im = PR.get_layer(name, scale, lit=True, t=0.4)
            assert im.width > 4 and im.height > 4, name
            assert im.getchannel("A").getextrema()[1] > 0, f"{name} пустая"
    a = PR.get_layer("fire", 0.5, t=0.0).tobytes()
    b = PR.get_layer("fire", 0.5, t=0.3).tobytes()
    assert a != b


def test_prop_aliases_and_colors():
    assert PR.resolve_prop("Automobile") == "car" and PR.resolve_prop("кошмар") is None
    assert PR.parse_color("#ff0000") == (255, 0, 0) and PR.parse_color("red") == PR.NAMED["red"]
    assert PR.parse_color("не цвет") is None and PR.parse_color([300, -5, 7]) == (255, 0, 7)


def test_normalize_spec_clamps_drops_and_caps():
    raw = {"bg": {"preset": "лава", "ground": "grass", "horizon": 9, "weather": "rain"},
           "objects": [{"prop": "летающий_слон", "x": 0.3},
                       {"prop": "man", "x": "левее", "y": 5, "scale": 99, "anim": [{"type": "bob"}, {"type": "explode"}, {"type": "fade_in"}, {"type": "pulse"}]},
                       {"prop": "cloud", "x": 2, "y": 0.9, "scale": 0.0},
                       {"prop": "pan", "on": "нет_такого"}] + [{"prop": "tree", "x": 0.1 * i} for i in range(30)],
           "camera": {"move": "teleport", "amount": 5}}
    spec, warn = DSL.normalize_spec(raw, "facts")
    assert spec["bg"]["preset"] == "plain" and spec["bg"]["horizon"] <= 0.58
    assert len(spec["objects"]) == DSL.MAX_OBJECTS
    man = spec["objects"][0]
    assert man["prop"] == "person" and man["y"] <= DSL.Y_MAX and man["x"] == 0.5
    assert man["scale"] * PR.REGISTRY["person"].h <= 1000 + 1e-6
    assert [a["type"] for a in man["anim"]] == ["bob", "fade_in", "pulse"]      # неизвестная анимация убрана, максимум 3
    cloud = spec["objects"][1]
    assert cloud["y"] <= 0.46 and cloud["x"] == 1.0 and cloud["scale"] >= 0.25
    assert spec["objects"][2]["on"] == ""                                         # опора не найдена
    assert spec["camera"] == {"move": "none", "amount": 0.15}
    assert any("неизвестна" in w for w in warn)


def test_normalize_spec_rejects_garbage():
    for bad in (None, "строка", [], {"objects": []}, {"objects": [{"prop": "x"}]}):
        assert DSL.normalize_spec(bad)[0] is None
    s, _ = DSL.normalize_spec({"objects": [{"prop": "tree"}], "bg": "не словарь"}, "horror_rules")
    assert s["bg"]["preset"] == "night"                 # ночной жанр -> ночь по умолчанию


def test_on_places_object_on_surface_and_draws_after_carrier():
    spec, _ = DSL.normalize_spec(GOOD)
    placed = DSL.resolve_positions(spec)
    names = [o["prop"] for o in placed]
    assert names.index("table") < names.index("pan") < len(names)
    table = next(o for o in placed if o["prop"] == "table")
    pan = next(o for o in placed if o["prop"] == "pan")
    surf = PR.surface_offset("table") * table["scale"] / 1920
    assert abs(pan["y"] - (table["y"] - surf)) < 1e-9 and abs(pan["x"] - (table["x"] - 0.05)) < 1e-9


def test_generated_scene_renders_with_every_background_ground_weather_and_camera():
    for bgp in DSL.BG_PRESETS:
        for ground in ("none", "grass", "road", "water"):
            spec, _ = DSL.normalize_spec({"bg": {"preset": bgp, "ground": ground, "weather": "rain" if ground == "road" else "snow"},
                                          "objects": [{"prop": "house", "x": 0.4, "y": 0.55, "lit": True,
                                                       "anim": [{"type": "sway"}, {"type": "flicker"}]},
                                                      {"prop": "bird", "x": 0.6, "y": 0.3, "anim": [{"type": "orbit", "cx": 0.5, "cy": 0.3, "r": 0.1}]}],
                                          "shapes": [{"type": "text", "text": "ПРИВЕТ", "x": 0.5, "y": 0.2},
                                                     {"type": "poly", "points": [[0.1, 0.1], [0.2, 0.1], [0.15, 0.2]]}],
                                          "camera": {"move": "push_in", "amount": 0.1}})
            beat = {"id": 1, "start": 0, "end": 3, "text": "t", "mode": "motion", "scene_spec": spec}
            plan = plan_storyboard({"beats": [beat]}, 3.0, preset="facts")
            for t in (0.0, 1.4, 2.9):
                assert draw_frame(plan, 0, t, 80).size == (80, 142)


def test_camera_moves_zoom_and_keep_size():
    from PIL import Image
    im = Image.new("RGB", (100, 180), (10, 20, 30))
    im.paste((255, 0, 0), (45, 80, 55, 100))
    for mv in ("push_in", "pull_out", "pan_left", "pan_right"):
        out = DSL.apply_camera(im, {"move": mv, "amount": 0.1}, 0.5)
        assert out.size == im.size
    assert DSL.apply_camera(im, {"move": "none", "amount": 0.1}, 0.5) is im


def test_lexicon_and_offline_designer_pick_props_from_words():
    assert [n for _p, n, _o in find_props("Выливаем смесь на сковороду и ставим чайник")][:1] == ["pan"]
    assert find_props("Абстрактная мысль без предметов") == []
    sp = D.heuristic_scene("Взбиваем яйца с молоком и выливаем на сковороду.", "facts")
    props = [o["prop"] for o in sp["objects"]]
    assert {"pan", "bottle", "table"} <= set(props) and sp["bg"]["preset"] == "indoor"
    assert any(o.get("on") == "c1" for o in sp["objects"])            # мелочь стоит на столе
    night = D.heuristic_scene("Ночью сосед стоит у забора возле дома.", "horror_rules")
    assert night["bg"]["preset"] == "night" and {"house", "fence", "person"} <= {o["prop"] for o in night["objects"]}
    space = D.heuristic_scene("Полёт к планете займёт семь лет.", "facts")
    assert space["bg"]["preset"] == "space" and space["bg"]["ground"] == "none"
    boat = D.heuristic_scene("Корабль плывёт по океану.", "facts")
    assert boat["bg"]["ground"] == "water" and boat["bg"]["preset"] != "underwater"
    assert D.heuristic_scene("Просто тишина.", "facts") is None
    assert D.heuristic_scene("Ракета стартует", "facts") == D.heuristic_scene("Ракета стартует", "facts")   # детерминированно
    for sp_ in (sp, night, space, boat):
        assert DSL.normalize_spec(sp_)[0] is not None


def test_designer_uses_llm_then_cache_and_retries_with_feedback():
    beat = {"id": 1, "text": "Взбиваем яйца и жарим омлет на сковороде", "mode": "motion", "scene_type": "custom"}
    ctx = {"preset": "facts", "title": "Рецепт", "provider": "qwen", "prev": "фон night"}
    calls = []
    thin = {"bg": {"preset": "indoor"}, "objects": [{"prop": "pan", "x": 0.5, "y": 0.55}]}       # одной детали мало
    spec, src, notes = D.design_scene(beat, ctx, llm=_llm(thin, GOOD, calls=calls))
    assert src == "llm" and len(calls) == 2 and "не подошла" in calls[1] and "слишком мало" in calls[1]
    assert "Предыдущая сцена" in calls[0] and "Рецепт" in calls[0]
    again, src2, _ = D.design_scene(beat, ctx, llm=_llm(RuntimeError("не должен вызываться")))
    assert src2 == "cache" and again == spec


def test_designer_falls_back_to_vocabulary_and_to_none():
    ctx = {"preset": "facts", "title": "т", "provider": "qwen"}
    beat = {"id": 1, "text": "Собака бежит по двору", "mode": "motion"}
    spec, src, notes = D.design_scene(beat, ctx, llm=_llm(ConnectionError("Ollama недоступна")), use_cache=False)
    assert src == "heuristic" and any("Ollama недоступна" in n for n in notes)
    spec, src, _ = D.design_scene(beat, ctx, llm=_llm("это не json вообще"), use_cache=False)
    assert src == "heuristic"
    empty = {"id": 2, "text": "Просто тишина.", "mode": "motion"}
    spec, src, _ = D.design_scene(empty, ctx, llm=_llm(ConnectionError("x")), use_cache=False)
    assert spec is None and src == "none"


def test_heuristic_mode_never_calls_llm():
    def boom(*a):
        raise AssertionError("LLM вызван в режиме heuristic")
    spec, src, _ = D.design_scene({"id": 1, "text": "Машина едет по дороге", "mode": "motion"},
                                  {"preset": "facts", "provider": "qwen"}, mode="heuristic", llm=boom, use_cache=False)
    assert src == "heuristic" and spec


def test_policy_which_beats_get_a_drawn_scene():
    w = D.wants_design
    assert w({"mode": "motion", "scene_type": "custom"}, "scene_type", "auto")
    assert w({"mode": "motion", "scene_type": ""}, "rotation", "auto")
    assert not w({"mode": "motion", "scene_type": "radio_alert"}, "scene_type", "auto")     # режиссёр выбрал готовую сцену
    assert not w({"mode": "kinetic", "scene_type": ""}, "rotation", "auto")                # крупный текст остаётся текстом
    assert not w({"mode": "motion", "scene_type": "end_card"}, "rotation", "all")
    assert w({"mode": "motion", "scene_type": "radio_alert"}, "scene_type", "all")
    assert not w({"mode": "motion", "scene_type": "custom"}, "scene_type", "off")
    assert not w({"mode": "motion", "scene_type": "custom", "scene_spec": {"x": 1}}, "scene_type", "all")


def test_design_scenes_fills_beats_and_reports_stats():
    beats = [
        {"id": 1, "start": 0, "end": 3, "text": "Он открывает книгу и читает вслух.", "mode": "motion", "scene_type": ""},
        {"id": 2, "start": 3, "end": 6, "text": "Просто тишина.", "mode": "motion", "scene_type": "custom"},
        {"id": 3, "start": 6, "end": 9, "text": "Радио молчит.", "mode": "motion", "scene_type": "radio_alert"},
        {"id": 4, "start": 9, "end": 12, "text": "Подпишись.", "mode": "motion", "scene_type": "end_card"},
    ]
    logs = []
    st = D.design_scenes(beats, "facts", "т", provider="qwen", mode="heuristic", log=logs.append, use_cache=False)
    assert st["requested"] == 2 and st["heuristic"] == 1 and st["none"] == 1
    assert beats[0]["_scene_source"] == "heuristic" and beats[0]["scene_spec"]["objects"]
    assert "scene_spec" not in beats[1] and "scene_spec" not in beats[2] and "scene_spec" not in beats[3]
    assert any("Художник сцен" in l for l in logs)
    assert D.design_scenes(beats, "facts", "т", mode="off")["requested"] == 0


def test_engine_uses_generated_spec_and_custom_without_spec_falls_back_to_text():
    b1 = {"id": 1, "start": 0, "end": 3, "text": "x", "mode": "motion", "scene_type": "custom",
          "scene_spec": D.heuristic_scene("Собака бежит по двору", "facts")}
    b2 = {"id": 2, "start": 3, "end": 6, "text": "Тут ничего", "mode": "motion", "scene_type": "custom", "title": "ТЕКСТ"}
    plan = plan_storyboard({"beats": [b1, b2]}, 6.0, preset="facts")
    assert (plan.beats[0].scene, plan.beats[0].reason) == ("generated", "generated")
    assert (plan.beats[1].scene, plan.beats[1].reason) == ("kinetic_text", "custom_no_spec")


def test_render_clip_with_generated_scenes_and_camera():
    import subprocess
    b = {"id": 1, "start": 0, "end": 1.0, "text": "x", "mode": "motion",
         "scene_spec": D.heuristic_scene("Ракета стартует на рассвете", "facts")}
    with tempfile.TemporaryDirectory() as d:
        out = render_plan(plan_storyboard({"beats": [b]}, 1.0, preset="facts"), Path(d) / "g.mp4", width=120, fps=30)
        n = subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries",
                            "stream=nb_read_frames", "-of", "csv=p=0", str(out)], capture_output=True, text=True).stdout.strip()
        assert int(n) == 30


def test_llm_schema_and_prompt_cover_the_whole_library():
    schema = D.build_schema()
    assert set(schema["properties"]["objects"]["items"]["properties"]["prop"]["enum"]) == set(PR.REGISTRY)
    json.dumps(schema)
    prompt = D.system_prompt()
    assert all(f"- {n} (" in prompt for n in PR.REGISTRY)
    beat_props = DL.STORYBOARD_SCHEMA["properties"]["beats"]["items"]["properties"]
    assert "custom" in beat_props["scene_type"]["enum"] and "visual" in beat_props
    assert "custom" in DL.DIRECTOR_SYSTEM_PROMPT and "visual" in DL.DIRECTOR_SYSTEM_PROMPT


def test_beat_the_designer_could_not_draw_shows_text_not_a_random_scene():
    b = {"id": 1, "start": 0, "end": 3, "text": "Просто тишина.", "mode": "motion", "scene_type": "", "title": "ТИШИНА",
         "_scene_source": "none"}
    assert plan_storyboard({"beats": [dict(b)]}, 3.0, preset="facts").beats[0].scene == "kinetic_text"
    # в сюжетных жанрах ночные сцены остаются запасными
    assert plan_storyboard({"beats": [dict(b)]}, 3.0, preset="horror_rules").beats[0].scene != "kinetic_text"


def test_person_poses_are_chosen_by_verbs_and_animate():
    for text, want in [("Мальчик бежит по дороге.", "person_run"), ("Девушка идёт через лес.", "person_walk"),
                       ("Старик сидит за столом.", "person_sit"), ("Он машет рукой на прощание.", "person_wave")]:
        sp = D.heuristic_scene(text, "facts")
        names = [o["prop"] for o in sp["objects"]]
        assert want in names and "person" not in names, (text, names)
    assert "person" in [o["prop"] for o in D.heuristic_scene("Человек стоит у дома.", "facts")["objects"]]
    for pose in ("person_walk", "person_run", "person_wave"):
        assert PR.REGISTRY[pose].dynamic
        assert PR.get_layer(pose, 0.5, t=0.0).tobytes() != PR.get_layer(pose, 0.5, t=0.2).tobytes(), pose
    assert not PR.REGISTRY["person_sit"].dynamic
