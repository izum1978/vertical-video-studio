import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.app.config import ROOT, OUTPUT, WORK
from backend.app import pipeline

job_id = "horror_cartoon_demo"
job = {
    "id": job_id,
    "status": "running",
    "stage": 0,
    "progress": 0,
    "logs": [],
}
req = {
    "topic": "Правила выживания на даче, если ровно в полночь пропала связь",
    "preset": "horror_rules",
    "lang": "ru",
    "voice": "ru-RU-DmitryNeural",
    "script": "mock",
    "tts": "edge",
    "visuals": "cartoon",
    "sub_style": "horror",
    "cta": "Вторая часть и секретные протоколы выживания по ссылке в шапке профиля 👆",
    "mock": False,
}

print("Starting pipeline test...")
pipeline._run(job, req)
print("Finished!")
for log in job["logs"]:
    print(log)
out_file = OUTPUT / f"{job_id}.mp4"
print(f"Output exists: {out_file.exists()}, size={out_file.stat().st_size if out_file.exists() else 0}")
