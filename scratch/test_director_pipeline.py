import os
import sys
import json
import shutil
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.config import OUTPUT, WORK
from app.pipeline import _run

def test_pipeline():
    sys.stdout.reconfigure(encoding="utf-8")
    print("=== ТЕСТИРОВАНИЕ ПОЛНОГО ПАЙПЛАЙНА С РЕЖИССЁРОМ (DIRECTOR) ===")
    job_id = "test_dir_01"
    job = {
        "id": job_id,
        "status": "running",
        "stage": 0,
        "logs": [],
        "video": None,
        "error": None,
    }
    req = {
        "topic": "3 правила выживания если выключили свет",
        "preset": "horror_rules",
        "script": "mock",
        "tts": "mock",
        "voice": "ru-RU-DmitryNeural",
        "visuals": "vector_2d",
        "lang": "ru",
        "sub_style": "horror",
        "mock": True,
        "cta": "Жми на колокольчик 💀",
    }

    _run(job, req)

    print("Статус задания:", job["status"])
    if job.get("error"):
        print("Ошибка:", job["error"])
        sys.exit(1)

    assert job["status"] == "done", f"Expected done, got {job['status']}"
    meta = job.get("video", {})
    assert "storyboard" in meta, "Storyboard not in metadata!"
    storyboard = meta["storyboard"]
    beats = storyboard.get("beats", [])
    print(f"Режиссёр сформировал {len(beats)} битов:")
    for b in beats:
        print(f"  Бит #{b.get('id')}: {b.get('start')}s - {b.get('end')}s [{b.get('mode')}] -> {b.get('title')}")

    out_file = OUTPUT / f"{job_id}.mp4"
    print(f"Видео сгенерировано: {out_file.exists()} (размер: {out_file.stat().st_size if out_file.exists() else 0} байт)")

    # УДАЛЯЕМ ВСЕ ТЕСТОВЫЕ ФАЙЛЫ, ЧТОБЫ НЕ ЗАСОРЯТЬ ПАМЯТЬ ПК ПОЛЬЗОВАТЕЛЯ!
    print("Удаляем тестовые артефакты...")
    if out_file.exists():
        out_file.unlink()
    json_file = OUTPUT / f"{job_id}.json"
    if json_file.exists():
        json_file.unlink()
    post_file = OUTPUT / f"{job_id}_post.txt"
    if post_file.exists():
        post_file.unlink()
    
    # Очищаем workdir
    job_work = WORK / job_id
    if job_work.exists():
        shutil.rmtree(job_work, ignore_errors=True)

    print("Все тестовые файлы удалены. Память чиста!")
    print("=== ТЕСТ ПРОЙДЕН УСПЕШНО ===")

if __name__ == "__main__":
    test_pipeline()
