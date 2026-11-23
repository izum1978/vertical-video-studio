"""Модуль Главного Кинорежиссера и Оператора-постановщика (Cinematic Director & DoP).

Отвечает за визуальную кинематографичность ролика:
1. Создает Cinematic Visual Continuity Bible (сквозной кино-стиль, свет, оптика 35mm, цветокоррекция).
2. Назначает операторскую работу (ракурсы, динамику камеры) для каждого бита сценария.
3. Формирует профессиональные англоязычные промпты и физику движения (motion_bucket_id)
   для диффузионной видеомодели Stable Video Diffusion.
"""
import hashlib
import json
import re
from pathlib import Path
from typing import Optional, Dict, Any, List

try:
    import httpx
except ImportError:
    import requests as httpx

from .config import env

CINEMATOGRAPHER_SYSTEM_PROMPT = (
    "You are a Hollywood Director of Photography and AI Cinematographer (Denis Villeneuve / Christopher Nolan aesthetic). "
    "Your job is to transform a video script into a cohesive, photorealistic, cinematic shot list for AI Video Diffusion.\n\n"
    "RULES OF CINEMATOGRAPHY:\n"
    "1. VISUAL STYLE: 100% Cinematic Realism, 35mm anamorphic film photography, dramatic volumetric atmosphere, "
    "rich organic textures, high dynamic range, master lighting. NO cartoons, NO flat 2D illustrations, NO cheap CGI.\n"
    "2. FULL SITUATIONAL COMPOSITION: Each frame must show the full physical environment, subjects, lighting interplay, and tangible atmosphere.\n"
    "3. SHOT VARIETY: Establish wide cinematic master shot -> tense medium POV -> hyper-detailed macro close-up -> dramatic low angle -> epic climax.\n"
    "4. MOTION & PHYSICS: Explicitly define physical movement (billowing smoke, fire exhaust, rushing motion, drifting embers, camera push-in).\n"
    "5. DYNAMIC INTENSITY (motion_bucket 120-220): High action/missiles/explosions = 180-220, suspense/waiting = 125-145.\n\n"
    "OUTPUT FORMAT: strictly valid JSON only:\n"
    '{"continuity":{"art_style":str,"palette":str,"mood":str,"lighting":str,"lens":str},'
    '"scenes":[{"id":int,"camera_shot":str,"camera_motion":str,"motion_bucket":int,"action_motion":str,"prompt":str}]}'
)

CINEMATIC_CONTINUITY_PRESETS = [
    {
        "art_style": "cinematic photorealistic thriller, 35mm anamorphic lens, Panavision framing, film grain",
        "palette": "cold desaturated steel blue, deep obsidian shadows with sudden fiery amber reflections",
        "mood": "intense palpable tension, high stakes realism, atmospheric suspense",
        "lighting": "harsh volumetric searchlights piercing stormy night clouds, pulsating emergency beacon glare",
        "lens": "anamorphic 35mm lens, shallow depth of field, subtle chromatic aberration",
    },
    {
        "art_style": "cinematic gritty neo-noir realism, IMAX photography, high dynamic contrast",
        "palette": "midnight cyan, wet asphalt mirror reflections, stark emergency flare crimson",
        "mood": "claustrophobic urban threat, urgent survival atmosphere",
        "lighting": "sodium vapor streetlight through rain, deep chiaroscuro contrast",
        "lens": "50mm master prime, cinematic framing, sharp organic details",
    },
    {
        "art_style": "epic documentary realism, BBC / National Geographic high budget cinematography",
        "palette": "naturalistic deep tones, overcast slate gray with vibrant emergency accent lights",
        "mood": "authentic historical weight, awe-inspiring scale",
        "lighting": "diffused overcast sky with sharp tactical spotlight highlights",
        "lens": "wide 24mm cinema lens, immersive perspective, sharp edge-to-edge fidelity",
    },
]


def establish_visual_continuity(topic: str, preset: str = "facts") -> dict:
    """Формирует визуальный паспорт непрерывности (Continuity Bible) ролика."""
    h = int(hashlib.md5(topic.encode("utf-8")).hexdigest(), 16) % 1000000
    chosen = CINEMATIC_CONTINUITY_PRESETS[h % len(CINEMATIC_CONTINUITY_PRESETS)]
    return {
        "seed": h,
        "art_style": chosen["art_style"],
        "palette": chosen["palette"],
        "mood": chosen["mood"],
        "lighting": chosen["lighting"],
        "lens": chosen["lens"],
    }


def query_ollama_cinematographer(script_text: str, beats: list[dict], preset: str) -> Optional[dict]:
    """Запрашивает у локальной LLM в Ollama кинематографическую раскадровку."""
    base_url = env("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    candidates = [
        env("OLLAMA_CINEMATOGRAPHER_MODEL", "qwen2.5-cinematographer:latest"),
        env("OLLAMA_CODER_MODEL", "qwen2.5-coder:7b"),
        env("OLLAMA_MODEL", "qwen2.5:7b"),
    ]

    user_payload = {
        "preset": preset,
        "script": script_text,
        "beats_count": len(beats),
        "beats_summary": [
            {"id": b["id"], "text": b.get("text", "")[:80], "title": b.get("title", "")}
            for b in beats
        ],
    }

    for model_name in candidates:
        try:
            r = httpx.post(
                f"{base_url}/chat/completions",
                json={
                    "model": model_name,
                    "messages": [
                        {"role": "system", "content": CINEMATOGRAPHER_SYSTEM_PROMPT},
                        {
                            "role": "user",
                            "content": f"Create cinematic DoP shot list for this video script:\n{json.dumps(user_payload, ensure_ascii=False)}",
                        },
                    ],
                    "temperature": 0.35,
                    "max_tokens": 1400,
                },
                timeout=3,
            )
            if r.status_code == 200:
                raw = r.json()["choices"][0]["message"]["content"]
                clean_json = re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.M).strip()
                parsed = json.loads(clean_json)
                if isinstance(parsed, dict) and "scenes" in parsed and isinstance(parsed["scenes"], list):
                    return parsed
        except Exception:
            continue

    return None


def direct_cinematography(script_data: dict, storyboard: dict) -> dict:
    """Главная функция Оператора-постановщика:
    
    Обогащает каждый бит раскадровки кино-ракурсами, описанием физики движения
    и параметрами интенсивности диффузии.
    """
    topic = script_data.get("topic", "событие")
    preset = script_data.get("preset", "facts")
    script_text = script_data.get("script", "")
    beats = storyboard.get("beats", [])

    continuity = establish_visual_continuity(topic, preset)
    seed = continuity["seed"]

    # 1. Пробуем получить умную раскадровку от нейросети Qwen в Ollama
    ai_plan = query_ollama_cinematographer(script_text, beats, preset)
    ai_scenes_map = {}
    if ai_plan:
        if "continuity" in ai_plan and isinstance(ai_plan["continuity"], dict):
            continuity.update(ai_plan["continuity"])
        for sc in ai_plan.get("scenes", []):
            if "id" in sc:
                ai_scenes_map[sc["id"]] = sc

    camera_shots = ["wide cinematic shot", "medium POV shot", "extreme macro close-up", "low angle dynamic shot", "dramatic push-in", "over-the-shoulder"]
    motions = ["zoom_in", "pan_down", "dramatic_push", "zoom_out", "pan_up"]

    enriched_beats = []
    for i, b in enumerate(beats):
        b_id = b.get("id", i + 1)
        sent_text = b.get("text", "")
        sub_title = b.get("title", "")

        ai_sc = ai_scenes_map.get(b_id, {})
        shot = ai_sc.get("camera_shot", camera_shots[i % len(camera_shots)])
        motion = ai_sc.get("camera_motion", motions[i % len(motions)])

        # Анализ динамики движения под конкретный бит
        raw_text = (sent_text + " " + sub_title + " " + topic).lower()
        if any(w in raw_text for w in ["ракет", "взрыв", "удар", "бег", "летит", "огонь"]):
            default_bucket = 185
            action_desc = "rapid physical motion, fiery rocket exhaust plume, billowing black smoke, camera shaking"
        elif any(w in raw_text for w in ["сирен", "тревог", "ноч", "город", "небо"]):
            default_bucket = 155
            action_desc = "pulsing red emergency beacon flares, atmospheric clouds drifting across night sky"
        else:
            default_bucket = 135
            action_desc = "slow cinematic camera dolly, subtle drifting dust particles in dramatic lighting"

        motion_bucket = ai_sc.get("motion_bucket", default_bucket)
        action_motion = ai_sc.get("action_motion", action_desc)

        cinematic_prompt = ai_sc.get("prompt")
        if not cinematic_prompt:
            cinematic_prompt = (
                f"Cinematic movie still of {topic}, scene: {sent_text or sub_title}. "
                f"{shot}, {continuity['art_style']}, {continuity['mood']}, "
                f"lighting: {continuity['lighting']}, color grade: {continuity['palette']}, {continuity['lens']}, "
                f"photorealistic physical motion: {action_motion}, vertical 9:16, masterpiece, ultra-detailed 8k"
            )

        b["camera_shot"] = shot
        b["motion"] = motion
        b["motion_bucket"] = motion_bucket
        b["visual_seed"] = seed + i
        b["cinematography_prompt"] = cinematic_prompt
        b["prompt"] = cinematic_prompt
        b["action_motion"] = action_motion
        enriched_beats.append(b)

    storyboard["beats"] = enriched_beats
    storyboard["continuity"] = continuity
    return storyboard
