"""Модуль сторителлинга и промптов (100% бесплатно).

Генерирует кинематографичные сценарии по структуре голливудских саспенс-триллеров:
1. Hook (крючок первых 2 секунд)
2. Tension (деталь, вызывающая тревогу)
3. Escalation (нарастание угрозы)
4. Cliffhanger (леденящий финал с удержанием внимания)

Для каждой сцены формируются:
- Русский текст озвучки
- Английский детальный промпт для Flux / Midjourney (35mm photorealism)
- Движение 2.5D камеры (push_in, pan, tilt)
- Звуковой эффект (SFX cue)
"""
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class CinematicScene:
    scene_id: int
    text_ru: str
    art_prompt: str
    camera_move: str = "push_in"
    sfx_cue: Optional[str] = None
    is_character: bool = False
    portrait_preset: str = "talking"


@dataclass
class CinematicStory:
    title: str
    category: str
    scenes: List[CinematicScene] = field(default_factory=list)

    @property
    def full_voiceover_text(self) -> str:
        return " ".join(s.text_ru for s in self.scenes)


# Коллекция вирусных кинематографичных сценариев (100% готовы к бесплатному продакшну)
CURATED_STORIES = [
    CinematicStory(
        title="Случай на ночной трассе",
        category="thriller",
        scenes=[
            CinematicScene(
                scene_id=1,
                text_ru="В полночь на глухой лесной трассе внезапно заглох двигатель.",
                art_prompt="night rural highway surrounded by dark towering pine forest, broken car with faint yellow headlights cutting through dense fog, 35mm film still",
                camera_move="push_in",
                sfx_cue="sub_boom",
            ),
            CinematicScene(
                scene_id=2,
                text_ru="Вокруг стояла мёртвая тишина, пока радио само не включилось на пустой частоте.",
                art_prompt="close up of vintage dusty car dashboard illuminated by eerie green radio dial glow, dark night outside car window, cinematic mystery",
                camera_move="pan_right",
                sfx_cue="glitch",
            ),
            CinematicScene(
                scene_id=3,
                text_ru="В зеркале заднего вида промелькнул силуэт, стоящий прямо у багажника.",
                art_prompt="car rearview mirror reflection showing tall dark hooded silhouette standing in road fog behind the car, cinematic suspense, Kodak Vision3",
                camera_move="push_in",
                sfx_cue="footstep_creak",
            ),
            CinematicScene(
                scene_id=4,
                text_ru="Но когда водитель обернулся... стекло с его стороны было уже открыто.",
                art_prompt="driver side car window rolled down into pitch black foggy forest, cold vapor breath, intense cinematic dread, David Fincher lighting",
                camera_move="pull_out",
                sfx_cue="whisper",
            ),
        ]
    ),
    CinematicStory(
        title="Забытый бункер 7",
        category="sci-fi-mystery",
        scenes=[
            CinematicScene(
                scene_id=1,
                text_ru="Под старым заброшенным заводом нашли герметичную стальную дверь.",
                art_prompt="massive rusted blast vault door deep inside underground brutalist concrete bunker, red warning light beam in dust, 35mm cinematic film",
                camera_move="tilt_down",
                sfx_cue="heavy_door_slam",
            ),
            CinematicScene(
                scene_id=2,
                text_ru="На датчиках внутри температура падала каждую минуту на десять градусов.",
                art_prompt="frost covered retro analog computer pressure dials and gauges in freezing dark laboratory, volumetric fog, blue cinematic shadows",
                camera_move="pan_left",
                sfx_cue="water_drip",
            ),
            CinematicScene(
                scene_id=3,
                text_ru="Камеры видеонаблюдения зафиксировали движение в глубине затопленного тоннеля.",
                art_prompt="flooded underground tunnel with rusted catwalks, ripples in black water, dark creature silhouette moving beneath the water surface, cinematic thriller",
                camera_move="push_in",
                sfx_cue="footstep_creak",
            ),
            CinematicScene(
                scene_id=4,
                text_ru="И в этот момент тяжёлый засов начал медленно подниматься изнутри.",
                art_prompt="close up of heavy mechanical steel door locking mechanism turning by itself from inside, sparks, dark cinematic realism",
                camera_move="pull_out",
                sfx_cue="sub_boom",
            ),
        ]
    ),
    CinematicStory(
        title="Шёпот в пустом доме",
        category="horror",
        scenes=[
            CinematicScene(
                scene_id=1,
                text_ru="В доме, где сорок лет никто не жил, в три часа ночи зажёгся свет на чердаке.",
                art_prompt="lonely old victorian wooden mansion on a foggy autumn hill at 3 AM, single warm ominous light burning in small attic window, cinematic realism",
                camera_move="push_in",
                sfx_cue="clock_tick",
            ),
            CinematicScene(
                scene_id=2,
                text_ru="Деревянная лестница скрипела под чьими-то тяжёлыми неторопливыми шагами.",
                art_prompt="narrow dark wooden spiraling staircase ascending into darkness, dusty light beam from attic doorway, suspense film still",
                camera_move="tilt_up",
                sfx_cue="footstep_creak",
            ),
            CinematicScene(
                scene_id=3,
                text_ru="Телефон на первом этаже внезапно зазвонил, хотя провода были обрезаны.",
                art_prompt="vintage rotary phone sitting on wooden table with clearly cut severed copper wire, cinematic low light, atmospheric dust particles",
                camera_move="pan_right",
                sfx_cue="glitch",
            ),
            CinematicScene(
                scene_id=4,
                text_ru="А из трубки донёсся твой собственный испуганный голос.",
                art_prompt="old telephone receiver floating off the hook, dark shadowy hallway background, psychological thriller film still, 8k Kodak",
                camera_move="push_in",
                sfx_cue="whisper",
            ),
        ]
    ),
    CinematicStory(
        title="Допрос свидетеля",
        category="character-thriller",
        scenes=[
            CinematicScene(
                scene_id=1,
                text_ru="В полночь дежурный следователь включил лампу в сырой комнате допроса.",
                art_prompt="dark gritty interrogation room illuminated by single harsh overhead swing lamp, concrete walls, 35mm neo-noir cinematography",
                camera_move="push_in",
                sfx_cue="heavy_door_slam",
            ),
            CinematicScene(
                scene_id=2,
                text_ru="Напротив сидел человек, который пропал тридцать лет назад на заброшенной станции.",
                art_prompt="close up portrait of weathered pale man with piercing eyes looking into camera, dramatic noir rim lighting, high detail cinematic face",
                camera_move="push_in",
                sfx_cue="heartbeat",
                is_character=True,
                portrait_preset="talking",
            ),
            CinematicScene(
                scene_id=3,
                text_ru="Он медленно поднял взгляд и тихо произнёс: они все ещё ждут там под снегом.",
                art_prompt="close up portrait of mysterious pale man in dark coat speaking, piercing eyes looking into camera, dark shadows, cinematic noir film still",
                camera_move="handheld_drift",
                sfx_cue="whisper",
                is_character=True,
                portrait_preset="talking",
            ),
            CinematicScene(
                scene_id=4,
                text_ru="И в эту секунду в коридоре выключился весь свет.",
                art_prompt="pitch black corridor with only tiny emergency red exit sign glowing in distance, eerie silhouette, atmospheric suspense",
                camera_move="push_in",
                sfx_cue="electric_flicker",
            ),
        ]
    ),
]


def get_story_by_title(title_or_query: str) -> CinematicStory:
    """Возвращает готовый сценарий по названию или первый подходящий."""
    for s in CURATED_STORIES:
        if title_or_query.lower() in s.title.lower() or title_or_query.lower() in s.category:
            return s
    return CURATED_STORIES[0]


def create_custom_story(title: str, beats: List[dict]) -> CinematicStory:
    """Создаёт сценарий из произвольного списка сцен."""
    scenes = []
    for idx, b in enumerate(beats, start=1):
        scenes.append(
            CinematicScene(
                scene_id=idx,
                text_ru=b.get("text_ru", ""),
                art_prompt=b.get("art_prompt", ""),
                camera_move=b.get("camera_move", "push_in"),
                sfx_cue=b.get("sfx_cue", "impact" if idx == 1 else "whoosh"),
                is_character=b.get("is_character", False),
                portrait_preset=b.get("portrait_preset", "talking"),
            )
        )
    return CinematicStory(title=title, category="custom", scenes=scenes)


if __name__ == "__main__":
    story = CURATED_STORIES[0]
    print(f"Сценарий: {story.title}")
    print(f"Текст озвучки ({len(story.full_voiceover_text.split())} слов):")
    print(story.full_voiceover_text)
    for s in story.scenes:
        print(f"[{s.scene_id}] Камера: {s.camera_move} | SFX: {s.sfx_cue} | Промпт: {s.art_prompt[:40]}...")

