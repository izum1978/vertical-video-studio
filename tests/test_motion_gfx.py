"""Тесты движка motion_gfx: планировщик, сцены, рендер, субтитры в стиле референса."""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app import render as R  # noqa: E402
from app.director import create_fallback_storyboard  # noqa: E402
from app.motion_gfx import plan_storyboard, render_plan  # noqa: E402
from app.motion_gfx.engine import LEGACY, SCENES, draw_frame  # noqa: E402
from app.scene_resolver import SCENE_CHOICES, SCENE_RENDERERS, normalize_scene_type, resolve_scene  # noqa: E402

BEATS = [
    {"id": 1, "start": 0.0, "end": 3.2, "text": "А по радио передали: в полночь отключат свет.", "mode": "motion", "scene_type": "radio_alert", "title": "", "subtitle": ""},
    {"id": 2, "start": 3.2, "end": 6.0, "text": "Живёт в этом лесу Лёва, 52 года, лесник.", "mode": "motion", "scene_type": "neighbor_fence", "title": "", "subtitle": ""},
    {"id": 3, "start": 6.0, "end": 9.5, "text": "Правило первое: тишина. Ни света, ни звука.", "mode": "motion", "scene_type": "sound_rings", "title": "ТИШИНА", "subtitle": "НИ СВЕТА, НИ ЗВУКА"},
    {"id": 4, "start": 9.5, "end": 13.0, "text": "Правило второе: лестница.", "mode": "motion", "scene_type": "ladder_house", "title": "ЛЕСТНИЦА", "subtitle": ""},
    {"id": 5, "start": 13.0, "end": 16.5, "text": "Но на третью ночь свет загорится.", "mode": "motion", "scene_type": "lit_window_house", "title": "ДОМ", "subtitle": "ПУСТОЙ"},
    {"id": 6, "start": 16.5, "end": 20.0, "text": "Часть вторая: кто в доме напротив. Подпишись.", "mode": "motion", "scene_type": "end_card", "title": "КТО В ДОМЕ НАПРОТИВ", "subtitle": ""},
]


def test_every_known_scene_name_maps_to_a_drawing():
    for name in SCENE_RENDERERS:
        assert LEGACY.get(name, name) in SCENES, name
    for name in SCENE_CHOICES:
        assert normalize_scene_type(name) == name and name in SCENES, name


def test_planner_chapters_person_day_label_and_end_card():
    plan = plan_storyboard({"beats": BEATS}, 20.0, preset="horror_rules")
    kinds = [[o["type"] for o in pb.overlays] for pb in plan.beats]
    assert kinds[1] == ["lower_third"]                         # «Лёва, 52 года, лесник»
    assert kinds[2] == ["chapter_card"] and kinds[3] == ["chapter_card"]
    nums = [o["num"] for pb in plan.beats for o in pb.overlays if o["type"] == "chapter_card"]
    assert nums == ["01", "02"]
    assert kinds[4] == []                                      # заголовок режиссёра без «Правило N» не даёт карточку
    assert plan.beats[4].label == "НОЧЬ 3"
    assert plan.beats[-1].scene == "end_card" and plan.beats[-1].beat["part_label"] == "часть 2"
    clocks = [pb.clock for pb in plan.beats]
    assert clocks[0] == "23:40" and clocks == sorted(clocks)


def test_planner_boundaries_are_continuous_and_cover_audio():
    plan = plan_storyboard({"beats": [dict(b) for b in BEATS]}, 21.5, preset="facts")
    assert plan.beats[0].start == 0.0 and plan.beats[-1].end >= 21.5
    assert all(abs(a.end - b.start) < 1e-6 for a, b in zip(plan.beats, plan.beats[1:]))


def test_hud_only_for_story_presets_unless_configured():
    assert plan_storyboard({"beats": BEATS}, 20, preset="facts").hud["enabled"] is False
    assert plan_storyboard({"beats": BEATS}, 20, preset="horror_rules").hud["enabled"] is True
    cfg = plan_storyboard({"beats": BEATS}, 20, preset="facts", hud={"enabled": True, "clock_start": "07:05", "status": "ЛАЙВ"})
    assert cfg.beats[0].clock == "07:05" and cfg.hud["status"] == "ЛАЙВ"


def test_story_keyword_rules_apply_only_to_story_presets():
    assert resolve_scene({"mode": "motion", "text": "Он набирает воду"}, "horror_rules", 0)[0] == "bathtub_water"
    assert resolve_scene({"mode": "motion", "text": "Вода на Земле"}, "facts", 0)[1] == "rotation"
    assert resolve_scene({"mode": "motion", "text": "На третью ночь"}, "horror_rules", 0)[0] == "night_village"
    assert resolve_scene({"mode": "motion", "text": "В сети ночь"}, "facts", 0)[0] == "city_night"


def test_fallback_storyboard_lets_resolver_choose_scenes():
    sb = create_fallback_storyboard("Включат свет. Он набирает воду. Трасса встанет. Но на третью ночь всё изменится.",
                                    16.0, preset="horror_rules", title="т")
    assert all(b["scene_type"] == "" for b in sb["beats"])
    plan = plan_storyboard(sb, 16.0, preset="horror_rules")
    assert {"bathtub_water", "highway_jam"} <= {pb.scene for pb in plan.beats}


def test_every_scene_draws_for_empty_long_and_list_beats():
    shapes = [{"text": "", "title": "", "subtitle": ""},
              {"text": "Очень длинная фраза про то, как мы делали сложное дело и что из этого вышло в итоге", "title": "ОЧЕНЬ ДЛИННЫЙ ЗАГОЛОВОК ИЗ МНОГИХ СЛОВ", "subtitle": "ПОДПИСЬ ТОЖЕ ДЛИННАЯ"},
              {"text": "В 2024 году выросло на 45%", "title": "45%", "items": ["раз", "два", "три", "четыре"]}]
    for name in SCENES:
        for beat in shapes:
            plan = plan_storyboard({"beats": [dict(beat, start=0.0, end=4.0, scene_type=name, mode="motion")]}, 4.0, preset="facts")
            for t in (0.05, 1.5, 3.9):
                im = draw_frame(plan, 0, t, 90)
                assert im.size == (90, 160)
    assert draw_frame(plan, 0, 1.0, 90).getextrema() != ((0, 0),) * 3


def test_render_clip_has_expected_duration_and_frames():
    with tempfile.TemporaryDirectory() as d:
        plan = plan_storyboard({"beats": [dict(b) for b in BEATS[:2]]}, 1.0, preset="horror_rules")
        out = render_plan(plan, Path(d) / "m.mp4", width=180, fps=30)
        p = subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0",
                            "-show_entries", "stream=width,height,nb_read_frames", "-of", "csv=p=0", str(out)],
                           capture_output=True, text=True)
        w, h, n = p.stdout.strip().split(",")
        assert (int(w), int(h)) == (180, 320) and int(n) == 30


def test_ref_subtitles_dim_future_words_and_color_accents():
    words = [{"word": w, "start": i * 0.4, "end": i * 0.4 + 0.35}
             for i, w in enumerate("А по радио передали, что ночью включат свет. Тишина.".split())]
    with tempfile.TemporaryDirectory() as d:
        out = R.build_ass("А по радио *передали*, что ночью включат !свет!. Тишина.", 5.0, Path(d) / "s.ass",
                          style_name="ref", preset="horror_rules", word_timestamps=words)
        txt = out.read_text(encoding="utf-8")
    assert "Style: Ref," in txt and "\\an5\\pos(540,1215)" in txt
    first = [l for l in txt.splitlines() if l.startswith("Dialogue")][0]
    assert R.REF_DIM in first and "ПЕРЕДАЛИ" in first      # слова фразы, которые ещё не прозвучали, приглушены
    assert R.REF_RED in txt and R.REF_YELLOW in txt
    for l in (x for x in txt.splitlines() if x.startswith("Dialogue")):
        shown = l.split("}", 2)[-1]
        assert len(shown.split()) <= 4 + 12                 # не больше 4 слов в фразе (метки цвета склеены)


def test_ref_subtitles_auto_accent_without_markup():
    words = [{"word": w, "start": i * 0.4, "end": i * 0.4 + 0.35} for i, w in enumerate("Мы живём в маленьком городе".split())]
    with tempfile.TemporaryDirectory() as d:
        txt = R.build_ass("Мы живём в маленьком городе", 3.0, Path(d) / "s.ass", style_name="ref",
                          preset="facts", word_timestamps=words).read_text(encoding="utf-8")
    assert R.REF_YELLOW in txt


def test_provider_renders_one_full_length_clip_and_records_reasons():
    from app.providers.motion_gfx import MotionGraphicsVisual
    os.environ["MOTION_WIDTH"] = "120"
    beats = [dict(b) for b in BEATS[:3]]
    with tempfile.TemporaryDirectory() as d:
        clips = MotionGraphicsVisual().fetch([], 3, Path(d), script_data={"beats": beats, "preset": "horror_rules", "duration": 9.5})
        assert len(clips) == 1 and clips[0].exists() and clips[0].stat().st_size > 1000
    assert [b["_renderer"] for b in beats] == ["radio_alert", "neighbor_fence", "sound_rings"]
    assert all(b["_renderer_reason"] == "scene_type" for b in beats)


def test_provider_works_without_beats():
    from app.providers.motion_gfx import MotionGraphicsVisual
    os.environ["MOTION_WIDTH"] = "120"
    with tempfile.TemporaryDirectory() as d:
        clips = MotionGraphicsVisual().fetch([], 3, Path(d), script_data={"script": "Первое. Второе. Третье.", "duration": 3.0})
        assert clips[0].exists()
