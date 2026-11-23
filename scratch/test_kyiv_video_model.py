import json
import time
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.app.config import OUTPUT, WORK
from backend.app.cinematographer import direct_cinematography
from backend.app.providers.visuals import AIVideoVisual
from backend.app.render import build_ass, probe_duration, render
from backend.app.sfx import extract_sfx_events

def run_kyiv_test():
    print("================================================================")
    print("  ТЕСТИРОВАНИЕ ЛОКАЛЬНОГО ВИДЕО-ПАЙПЛАЙНА: ТЕМА 'КИЕВ'")
    print("================================================================")

    # 1. Загружаем эталонный сценарий и раскадровку
    source_json = OUTPUT / "6c82805c.json"
    if not source_json.exists():
        print(f"Файл {source_json} не найден!")
        return

    meta = json.loads(source_json.read_text(encoding="utf-8"))
    workdir = WORK / "kyiv_ai_video_test"
    workdir.mkdir(parents=True, exist_ok=True)

    # Копируем проверенную аудиодорожку и таймкоды слов
    cached_audio = WORK / "6c82805c" / "voice.mp3"
    voice_file = workdir / "voice.mp3"
    if not voice_file.exists() and cached_audio.exists():
        voice_file.write_bytes(cached_audio.read_bytes())

    cached_words = WORK / "6c82805c" / "voice.words.json"
    word_timestamps = None
    if cached_words.exists():
        word_timestamps = json.loads(cached_words.read_text(encoding="utf-8"))

    dur = probe_duration(voice_file)
    print(f"1. Озвучка: {dur:.1f} сек. Загружено {len(word_timestamps or [])} меток слов.")

    # 2. Обогащаем раскадровку операторским планом и динамическими промптами
    print("2. Оператор-постановщик: обогащение сцен дескрипторами динамики...")
    storyboard = meta.get("storyboard", {})
    sc_data = {
        "topic": meta.get("topic", "Что делать если в Киев летят баллистические ракеты"),
        "preset": meta.get("preset", "facts"),
        "script": meta.get("script", ""),
    }
    storyboard = direct_cinematography(sc_data, storyboard)
    beats = storyboard.get("beats", [])
    print(f"   Подготовлено сцен (битов): {len(beats)}")

    # 3. Генерация динамических видеосцен через AIVideoVisual
    print("3. Генерация динамических видеосцен (AI Video Engine на GPU)...")
    sc_data["beats"] = beats
    sc_data["preset"] = meta.get("preset", "facts")

    t_vis = time.time()
    visual = AIVideoVisual()
    clips = visual.fetch(meta.get("keywords", []), len(beats), workdir, script_data=sc_data)
    dt_vis = time.time() - t_vis
    print(f"   Все клипы сгенерированы за {dt_vis:.1f} сек ({len(clips)} шт).")

    for i, c in enumerate(clips):
        print(f"   - Сцена {i+1}: {c.name} ({c.stat().st_size / (1024*1024):.2f} МБ)")

    # 4. Сборка субтитров
    print("4. Генерация субтитров (ASS Karaoke)...")
    ass_path = workdir / "subs.ass"
    sub_style = meta.get("sub_style", "mrbeast")
    build_ass(
        meta["script"],
        dur,
        ass_path,
        style_name=sub_style,
        preset=meta.get("preset", "facts"),
        word_timestamps=word_timestamps,
        hook_text=meta.get("hook", ""),
        cta_text=meta.get("cta", ""),
    )

    # 5. Сведение звука и SFX
    print("5. Извлечение SFX маркеров и сведение...")
    sfx_events = extract_sfx_events(
        meta["script"],
        dur,
        scenes=beats,
        word_timestamps=word_timestamps,
        preset=meta.get("preset", "facts"),
    )
    print(f"   Звуковые эффекты: {len(sfx_events)} SFX маркеров")

    # 6. Финальный рендеринг вертикального ролика 9:16
    out_mp4 = OUTPUT / "kyiv_ai_video_final.mp4"
    print(f"6. Финальный рендер 1080x1920 (60 FPS) в {out_mp4.name}...")
    t_rnd = time.time()
    render(
        clips,
        voice_file,
        ass_path,
        out_mp4,
        dur,
        workdir,
        preset=meta.get("preset", "facts"),
        sfx_events=sfx_events,
        progress_bar=True,
    )
    dt_rnd = time.time() - t_rnd

    print("================================================================")
    print(f"  ГОТОВО! Итоговый видеоролик успешно создан:")
    print(f"  Файл:      {out_mp4}")
    print(f"  Размер:    {out_mp4.stat().st_size / (1024*1024):.2f} МБ")
    print(f"  Рендер:    {dt_rnd:.1f} сек")
    print(f"  Длительность: {dur:.1f} сек")
    print("================================================================")

if __name__ == "__main__":
    run_kyiv_test()

