"""Оркестратор: Сценарий -> Озвучка -> Визуал -> Рендеринг. Очередь из одного воркера."""
import json
import math
import re
import time
import uuid
from concurrent.futures import ThreadPoolExecutor

from . import providers as P
from .config import OUTPUT, WORK
from .director import direct_storyboard
from .cinematographer import direct_cinematography
from .render import build_ass, probe_duration, render
from .sfx import extract_sfx_events

MOTION_STYLES = ("motion_gfx", "vector_2d", "cartoon", "2d_cartoon", "reference", "motion")
STAGES = ["Сценарий", "Озвучка", "Загрузка визуала", "Рендеринг", "Готово"]
_pool = ThreadPoolExecutor(max_workers=1)
JOBS: dict[str, dict] = {}
BATCHES: dict[str, dict] = {}


def _log(job, msg):
    job["logs"].append(f"{time.strftime('%H:%M:%S')}  {msg}")


def _run(job: dict, req: dict) -> None:
    try:
        mock = req.get("mock", False)
        pick = lambda name: "mock" if mock else name  # noqa: E731
        wd = WORK / job["id"]
        wd.mkdir(parents=True, exist_ok=True)

        lang = req.get("lang", "ru")
        preset = req.get("preset", "facts")
        topic = req.get("topic", "Видео")

        job["stage"] = 0
        _log(job, "Генерируем сценарий…")
        sc = P.get(P.SCRIPTS, pick(req.get("script", "qwen"))).generate(topic, preset, lang)
        _log(job, f"Хук: {sc['hook']}")

        job["stage"] = 1
        _log(job, "Синтезируем озвучку…")
        clean_script = re.sub(r"\[sfx:\s*\w+\]", "", sc["script"], flags=re.I)
        clean_script = re.sub(r"[*!]", "", clean_script)
        audio = P.get(P.TTS, pick(req.get("tts", "edge"))).synth(clean_script, req.get("voice", ""), lang, wd / "voice.mp3")
        dur = probe_duration(audio)
        _log(job, f"Озвучка готова: {dur:.1f} с")

        words_file = wd / "voice.words.json"
        word_timestamps = None
        if words_file.exists():
            try:
                word_timestamps = json.loads(words_file.read_text(encoding="utf-8"))
            except Exception:
                pass

        sub_style = req.get("sub_style", "mrbeast")
        preset = req.get("preset", "facts")
        vis_req = req.get("visuals", "motion_gfx")
        is_motion = vis_req in MOTION_STYLES
        if preset == "horror_rules" and sub_style == "mrbeast":
            sub_style = "horror"
        if is_motion and sub_style in ("mrbeast", "horror"):
            sub_style = "ref"   # подпись как в референсе: слова по порядку, будущие приглушены

        job["stage"] = 2
        _log(job, "Qwen Режиссёр: формируем монтажную раскадровку битов…")
        storyboard = direct_storyboard(
            sc,
            word_timestamps=word_timestamps,
            total_duration=dur,
            preset=preset,
            provider_name=pick(req.get("script", "qwen_local")),
            mock=mock,
            log=lambda m: _log(job, m),
        )
        if not is_motion:
            # Оператор-постановщик пишет англоязычные промпты для генератора картинок и видео.
            # Движку motion_gfx они не нужны, поэтому лишний вызов модели пропускаем.
            storyboard = direct_cinematography(sc, storyboard)
        beats = storyboard.get("beats", [])
        d = storyboard.get("meta", {}).get("director", {})
        _log(job, f"Раскадровка: источник={d.get('source')}, модель={d.get('model')}, "
                  f"попыток={d.get('attempts')}, битов={len(beats)}")
        scene_stats = None
        if is_motion:
            # Художник сцен: для битов, где готовой сцены мало, рисует новую под фразу (LLM, затем словарь)
            scene_mode = req.get("scene_gen", "auto")
            if mock and scene_mode == "auto":
                scene_mode = "heuristic"          # мок-режим не ходит в модели
            if scene_mode != "off":
                from .motion_gfx.designer import design_scenes
                scene_stats = design_scenes(beats, preset, sc.get("title", ""), provider=pick(req.get("script", "qwen_local")),
                                            mode=scene_mode, log=lambda m: _log(job, m))

        count = max(len(beats), max(3, min(12, round(dur / 4))))
        if is_motion:
            vis_prov = P.get(P.VISUALS, "motion_gfx")
        elif vis_req == "ai_video":
            vis_prov = P.get(P.VISUALS, "ai_video")
        elif vis_req in ("ai_scenes", "auto"):
            vis_prov = P.get(P.VISUALS, "ai_scenes")
        else:
            vis_prov = P.get(P.VISUALS, "ai_video")

        sc_data = dict(sc)
        sc_data["preset"] = preset
        sc_data["beats"] = beats
        sc_data["duration"] = dur
        sc_data["cta"] = req.get("cta", "")
        sc_data["hud"] = storyboard.get("hud") or req.get("hud")
        try:
            clips = vis_prov.fetch(sc.get("keywords", []), count, wd, script_data=sc_data)
        except TypeError:
            clips = vis_prov.fetch(sc.get("keywords", []), count, wd)

        from collections import Counter
        reasons = Counter(str(b.get("_renderer_reason", "n/a")).split(":")[0] for b in beats)
        _log(job, f"Выбор сцен по причинам: {dict(reasons)}")

        # Предупреждение Ф9: проверка доли fallback в последних 20 заданиях
        try:
            recent_metas = library()[:20]
            if recent_metas:
                fb_count = sum(1 for m in recent_metas if (m.get("director") or {}).get("source") == "fallback")
                fb_rate = fb_count / len(recent_metas)
                if fb_rate > 0.10:
                    _log(job, f"ВНИМАНИЕ: Доля fallback режиссёра за последние {len(recent_metas)} заданий: {fb_rate*100:.0f}% (>10%)! Проверьте Ollama и OLLAMA_DIRECTOR_MODEL.")
        except Exception:
            pass
        cta = req.get("cta", "")

        ass = build_ass(
            sc["script"],
            dur,
            wd / "subs.ass",
            style_name=sub_style,
            preset=preset,
            word_timestamps=word_timestamps,
            hook_text=sc.get("hook", ""),
            cta_text=cta,
        )

        job["stage"] = 3
        _log(job, "Сводим аудио с дакингом, SFX и прогресс-баром…")
        sfx_events = extract_sfx_events(
            sc["script"],
            dur,
            scenes=sc.get("scenes", []),
            word_timestamps=word_timestamps,
            preset=preset,
        )
        _log(job, f"Звуковые эффекты: {len(sfx_events)} SFX маркеров")

        out = OUTPUT / f"{job['id']}.mp4"
        if is_motion:
            render(clips, audio, ass, out, dur, wd, preset=preset, sfx_events=sfx_events,
                   progress_bar=False, fps=30, clean=True)
        else:
            render(clips, audio, ass, out, dur, wd, preset=preset, sfx_events=sfx_events, progress_bar=True)
        post_caption = sc.get("post_caption", sc.get("title", req["topic"]))
        hashtags = sc.get("hashtags", ["факты", "рек", "fyp", "тренды", "шортс"])
        tags_str = " ".join("#" + t.lstrip("#") for t in hashtags)

        post_text = (
            f"🎬 {sc.get('title', req['topic'])}\n\n"
            f"📌 {post_caption}\n\n"
            f"👉 {cta}\n\n"
            f"{tags_str}"
        )
        (OUTPUT / f"{job['id']}_post.txt").write_text(post_text, encoding="utf-8")

        meta = {
            "id": job["id"],
            "title": sc.get("title", req["topic"]),
            "hook": sc.get("hook", ""),
            "script": sc.get("script", ""),
            "keywords": sc.get("keywords", []),
            "topic": req["topic"],
            "preset": req.get("preset", "facts"),
            "lang": req.get("lang", "ru"),
            "sub_style": sub_style,
            "duration": round(dur, 1),
            "created": time.strftime("%Y-%m-%d %H:%M"),
            "url": f"/output/{job['id']}.mp4",
            "post_caption": post_caption,
            "hashtags": hashtags,
            "cta": cta,
            "post_text": post_text,
            "sfx_count": len(sfx_events),
            "progress_bar": not is_motion,
            "visuals": vis_req,
            "storyboard": storyboard,
            "director": storyboard.get("meta", {}).get("director"),
            "scene_gen": scene_stats,
            "scene_reasons": dict(reasons),
        }
        (OUTPUT / f"{job['id']}.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

        job.update(stage=4, status="done", video=meta)
        _log(job, "Готово!")
    except Exception as e:  # noqa: BLE001 — показываем причину в UI
        job.update(status="error", error=str(e))
        _log(job, f"ОШИБКА: {e}")


def _run_batch(batch: dict, req: dict, topics: list[str]) -> None:
    for idx, topic in enumerate(topics):
        batch["current_index"] = idx + 1
        batch["current_topic"] = topic
        job_req = dict(req)
        job_req["topic"] = topic
        job = {"id": uuid.uuid4().hex[:8], "status": "running", "stage": 0, "logs": [], "video": None, "error": None}
        JOBS[job["id"]] = job
        batch["jobs"].append(job["id"])
        _run(job, job_req)
        if job.get("status") == "done":
            batch["completed"] += 1
        else:
            batch["failed"] += 1
    batch["status"] = "done"


def submit(req: dict) -> dict:
    job = {"id": uuid.uuid4().hex[:8], "status": "running", "stage": 0, "logs": [], "video": None, "error": None}
    JOBS[job["id"]] = job
    _pool.submit(_run, job, req)
    return job


def submit_batch(req: dict) -> dict:
    raw_topics = req.get("topics", [])
    topics = [t.strip() for t in raw_topics if t and t.strip()]
    if not topics:
        raise ValueError("Список тем не может быть пустым")

    batch_id = uuid.uuid4().hex[:8]
    batch = {
        "id": batch_id,
        "status": "running",
        "total": len(topics),
        "completed": 0,
        "failed": 0,
        "current_index": 0,
        "current_topic": "",
        "jobs": [],
        "created": time.strftime("%Y-%m-%d %H:%M"),
    }
    BATCHES[batch_id] = batch
    _pool.submit(_run_batch, batch, req, topics)
    return batch


def get_job(job_id: str) -> dict | None:
    return JOBS.get(job_id)


def get_batch(batch_id: str) -> dict | None:
    return BATCHES.get(batch_id)


def library() -> list[dict]:
    items = []
    for p in OUTPUT.glob("*.json"):
        try:
            items.append(json.loads(p.read_text(encoding="utf-8")))
        except Exception:
            continue
    return sorted(items, key=lambda m: m.get("created", ""), reverse=True)


def delete_video(video_id: str) -> bool:
    found = False
    for ext in (".mp4", ".json", "_post.txt"):
        target = OUTPUT / f"{video_id}{ext}"
        if target.exists():
            target.unlink(missing_ok=True)
            found = True
    return found
