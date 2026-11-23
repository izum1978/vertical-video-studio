import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.app.providers.visuals import AIVideoVisual

workdir = ROOT / "output" / "test_ai_video_pipeline"
workdir.mkdir(parents=True, exist_ok=True)

test_script_data = {
    "topic": "Баллистическая тревога",
    "preset": "horror_rules",
    "beats": [
        {
            "id": 1,
            "text": "Если ночью зазвучала сирена, не подходите к окнам.",
            "prompt": "Night city Kyiv emergency siren red beacon lights, silhouettes near windows",
            "cinematography_prompt": "2D animated dark illustration of Kyiv night city red emergency siren lights",
            "motion": "dramatic_push",
            "action_motion": "rapid pulsing red beacon flares, dark clouds gathering over buildings",
            "duration": 3.2,
        },
        {
            "id": 2,
            "text": "Спускайтесь в ближайшее подземное укрытие за две минуты.",
            "prompt": "Crowd rushing underground subway bomb shelter entrance, heavy steel blast doors",
            "cinematography_prompt": "2D animated dark illustration of people rushing into underground shelter blast doors",
            "motion": "pan_down",
            "action_motion": "crowd rushing frantically into shelter entrance, dust and motion blur",
            "duration": 3.0,
        }
    ]
}

print("Running AIVideoVisual.fetch()...")
visual = AIVideoVisual()
clips = visual.fetch([], count=2, workdir=workdir, script_data=test_script_data)

print("Generated clips:")
for c in clips:
    print(f" -> {c} (exists: {c.exists()}, size: {c.stat().st_size} bytes)")

