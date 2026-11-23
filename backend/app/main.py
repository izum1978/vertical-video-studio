import asyncio
import json
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import pipeline
from . import providers as P
from .config import OUTPUT, check_ffmpeg
from .providers.script import LANGS, PRESETS
from .providers.tts import VOICES


@asynccontextmanager
async def lifespan(_: FastAPI):
    check_ffmpeg()
    yield


app = FastAPI(title="Vertical Video Studio", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.mount("/output", StaticFiles(directory=OUTPUT), name="output")


from .render import SUBTITLE_STYLES


class JobRequest(BaseModel):
    topic: str = Field(min_length=3)
    preset: str = "facts"
    lang: str = "ru"
    voice: str = ""
    script: str = "qwen"
    tts: str = "edge"
    visuals: str = "motion_gfx"
    scene_gen: str = "auto"          # художник сцен: auto | all | heuristic | off
    sub_style: str = "mrbeast"
    cta: str = "Ссылка в шапке профиля 👆"
    mock: bool = False


class BatchJobRequest(BaseModel):
    topics: list[str] = Field(min_length=1)
    preset: str = "facts"
    lang: str = "ru"
    voice: str = ""
    script: str = "qwen"
    tts: str = "edge"
    visuals: str = "motion_gfx"
    scene_gen: str = "auto"          # художник сцен: auto | all | heuristic | off
    sub_style: str = "mrbeast"
    cta: str = "Ссылка в шапке профиля 👆"
    mock: bool = False


@app.get("/api/options")
def options():
    return {
        "presets": [{"id": k, "label": v[0], "desc": v[1]} for k, v in PRESETS.items()],
        "langs": [{"id": k, "label": v} for k, v in LANGS.items()],
        "voices": {k: [{"id": i, "label": n} for i, n in v] for k, v in VOICES.items()},
        "sub_styles": [{"id": k, "label": v["label"]} for k, v in SUBTITLE_STYLES.items()],
        "script": [k for k in P.SCRIPTS if k != "mock"],
        "tts": [k for k in P.TTS if k != "mock"],
        "visuals": [k for k in P.VISUALS if k != "mock"],
        "stages": pipeline.STAGES,
    }


@app.post("/api/jobs")
def create_job(req: JobRequest):
    for reg, name in ((P.SCRIPTS, req.script), (P.TTS, req.tts), (P.VISUALS, req.visuals)):
        if name not in reg:
            raise HTTPException(400, f"Неизвестный провайдер: {name}")
    return pipeline.submit(req.model_dump())


@app.post("/api/batch")
def create_batch(req: BatchJobRequest):
    for reg, name in ((P.SCRIPTS, req.script), (P.TTS, req.tts), (P.VISUALS, req.visuals)):
        if name not in reg:
            raise HTTPException(400, f"Неизвестный провайдер: {name}")
    try:
        return pipeline.submit_batch(req.model_dump())
    except ValueError as e:
        raise HTTPException(400, str(e))


@app.get("/api/batch/{batch_id}")
def get_batch_status(batch_id: str):
    batch = pipeline.get_batch(batch_id)
    if not batch:
        raise HTTPException(404, "Пакетная задача не найдена")
    return batch


@app.get("/api/batch/{batch_id}/events")
async def batch_events(batch_id: str):
    batch = pipeline.BATCHES.get(batch_id)
    if not batch:
        raise HTTPException(404, "Пакетная задача не найдена")

    async def stream():
        last = None
        while True:
            # Prepare rich snapshot including current active job logs if any
            cur_job_id = batch["jobs"][-1] if batch.get("jobs") else None
            cur_job = pipeline.JOBS.get(cur_job_id) if cur_job_id else None
            payload = {
                "batch": batch,
                "current_job": cur_job,
            }
            snap = json.dumps(payload, ensure_ascii=False)
            if snap != last:
                last = snap
                yield f"data: {snap}\n\n"
            if batch["status"] != "running":
                break
            await asyncio.sleep(0.5)

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/api/jobs/{job_id}")
def get_job_status(job_id: str):
    job = pipeline.get_job(job_id)
    if not job:
        raise HTTPException(404, "Задача не найдена")
    return job


@app.get("/api/jobs/{job_id}/events")
async def events(job_id: str):
    job = pipeline.JOBS.get(job_id)
    if not job:
        raise HTTPException(404, "Задача не найдена")

    async def stream():
        last = None
        while True:
            snap = json.dumps(job, ensure_ascii=False)
            if snap != last:
                last = snap
                yield f"data: {snap}\n\n"
            if job["status"] != "running":
                break
            await asyncio.sleep(0.4)

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/api/videos")
def videos():
    return pipeline.library()


@app.delete("/api/videos/{video_id}")
def remove_video(video_id: str):
    ok = pipeline.delete_video(video_id)
    if not ok:
        raise HTTPException(404, "Видео не найдено")
    return {"ok": True, "id": video_id}


# -------------------------------------------------------------
# Кинематографичный AI-пайплайн (100% бесплатно)
# -------------------------------------------------------------
from .cinematic.assembler import assemble_cinematic_video
from .cinematic.story import CURATED_STORIES, get_story_by_title, create_custom_story


class CinematicJobRequest(BaseModel):
    story_title: str = "Случай на ночной трассе"
    custom_scenes: list[dict] = None


@app.get("/api/cinematic/stories")
def list_cinematic_stories():
    return [
        {
            "title": s.title,
            "category": s.category,
            "scenes_count": len(s.scenes),
            "preview_text": s.full_voiceover_text[:120] + "...",
        }
        for s in CURATED_STORIES
    ]


@app.post("/api/cinematic/generate")
def generate_cinematic(req: CinematicJobRequest):
    if req.custom_scenes:
        story = create_custom_story(req.story_title, req.custom_scenes)
    else:
        story = get_story_by_title(req.story_title)

    out_dir = OUTPUT / "cinematic_master"
    video_file = assemble_cinematic_video(story, out_dir=out_dir)
    return {
        "ok": True,
        "title": story.title,
        "video_path": str(video_file),
        "url": f"/output/cinematic_master/{video_file.name}",
    }

