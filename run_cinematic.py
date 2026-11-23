"""Кинематографичная AI-видеостудия (100% бесплатно).

Запуск генерации вирусных вертикальных видеороликов (9:16, 1080x1920)
в стиле темного кинематографичного реализма:
- 35mm пленочный арт
- 2.5D движения камеры с живым пленочным зерном
- Густой низкий голос диктора с пословными таймкодами
- Саунд-дизайн (суб-басовый эмбиент + SFX)
- Вирусные караоке-субтитры с золотой подсветкой

Использование:
  python run_cinematic.py
  python run_cinematic.py --story "Забытый бункер 7"
  python run_cinematic.py --list
"""
import argparse
import os
import sys
from pathlib import Path

# Добавляем корень проекта в sys.path
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app.cinematic.assembler import assemble_cinematic_video
from backend.app.cinematic.clipper import auto_clip_and_sub
from backend.app.cinematic.story import CURATED_STORIES, get_story_by_title


def main():
    parser = argparse.ArgumentParser(description="100% Бесплатная Кинематографичная AI-видеостудия")
    parser.add_argument(
        "--story",
        type=str,
        default=None,
        help="Название сценария или ключевое слово (например: 'ночной трассе', 'бункер', 'дом')",
    )
    parser.add_argument(
        "--clip",
        type=str,
        default=None,
        help="Путь к исходному видео для авто-нарезки, вертикального кропа 9:16 и авто-субтитров",
    )
    parser.add_argument(
        "--portrait",
        type=str,
        default=None,
        help="Путь к изображению лица для оживления через LivePortrait в вертикальное видео 9:16",
    )
    parser.add_argument(
        "--preset",
        type=str,
        default="talking",
        choices=["talking", "reaction", "subtle"],
        help="Пресет анимации лица: talking (речь), reaction (реакция), subtle (микромимика)",
    )
    parser.add_argument(
        "--upscale",
        type=str,
        default=None,
        help="Путь к изображению для локального нейросетевого апскейлинга до 4K через Real-ESRGAN",
    )
    parser.add_argument(
        "--4k",
        dest="enable_4k",
        action="store_true",
        help="Активировать 4K нейросетевой апскейлинг всех кадров при сборке видео",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=30.0,
        help="Максимальная длительность клипа при использовании --clip (по умолчанию 30с)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Показать список доступных готовых кинематографичных сценариев",
    )
    parser.add_argument(
        "--out",
        type=str,
        default=str(ROOT / "output" / "cinematic_master"),
        help="Директория сохранения готового видео",
    )
    parser.add_argument(
        "--open",
        action="store_true",
        help="Автоматически открыть готовое видео в плеере",
    )
    args = parser.parse_args()

    # Режим авто-клиппера
    if args.clip:
        clip_src = Path(args.clip)
        if not clip_src.exists():
            print(f"[Ошибка] Исходное видео не найдено: {clip_src}")
            return
        out_dir = Path(args.out)
        final_video = auto_clip_and_sub(clip_src, out_dir=out_dir, max_duration=args.duration)
        print("\n🎉 ГОТОВЫЙ ВЕРТИКАЛЬНЫЙ КЛИП:")
        print(f"   Видео: file:///{final_video.resolve().as_posix()}")
        if args.open:
            try:
                os.startfile(str(final_video))
            except Exception:
                pass
        return

    # Режим LivePortrait оживления портрета
    if args.portrait:
        portrait_src = Path(args.portrait)
        if not portrait_src.exists():
            print(f"[Ошибка] Файл портрета не найден: {portrait_src}")
            return
        out_dir = Path(args.out)
        out_dir.mkdir(parents=True, exist_ok=True)
        final_video = out_dir / f"portrait_live_{portrait_src.stem}_{args.preset}.mp4"
        print(f"\n🎭 Оживление лица через LivePortrait (пресет: {args.preset}, длительность: {args.duration:.1f}с)...")
        from backend.app.cinematic.portrait import animate_character_portrait
        animate_character_portrait(
            image_path=portrait_src,
            duration=args.duration,
            preset=args.preset,
            out_path=final_video,
        )
        print("\n🎉 ГОТОВЫЙ АНИМИРОВАННЫЙ ПЕРСОНАЖ 9:16:")
        print(f"   Видео: file:///{final_video.resolve().as_posix()}")
        if args.open:
            try:
                os.startfile(str(final_video))
            except Exception:
                pass
        return

    # Режим нейросетевого апскейла Real-ESRGAN до 4K
    if args.upscale:
        upscale_src = Path(args.upscale)
        if not upscale_src.exists():
            print(f"[Ошибка] Исходное изображение не найдено: {upscale_src}")
            return
        out_dir = Path(args.out)
        out_dir.mkdir(parents=True, exist_ok=True)
        final_img = out_dir / f"{upscale_src.stem}_4k.jpg"
        print(f"\n✨ Локальный нейросетевой апскейлинг Real-ESRGAN x4plus (4K UHD) на RTX GPU...")
        from backend.app.cinematic.upscaler import upscale_image_4k
        upscale_image_4k(upscale_src, out_path=final_img, scale=4)
        print("\n🎉 ГОТОВОЕ 4K ИЗОБРАЖЕНИЕ:")
        print(f"   Файл: file:///{final_img.resolve().as_posix()}")
        if args.open:
            try:
                os.startfile(str(final_img))
            except Exception:
                pass
        return

    if args.list:
        print("\n🎬 ДОСТУПНЫЕ ГОТОВЫЕ СЦЕНАРИИ:")
        for idx, s in enumerate(CURATED_STORIES, start=1):
            chars = sum(1 for sc in s.scenes if getattr(sc, "is_character", False))
            char_tag = f" | 🎭 LivePortrait персонажи: {chars}" if chars > 0 else ""
            print(f"  {idx}. [{s.category.upper()}] {s.title} ({len(s.scenes)} сцен{char_tag})")
            print(f"     Превью: \"{s.scenes[0].text_ru}\"")
        return

    # Выбор сценария
    if args.story:
        story = get_story_by_title(args.story)
    else:
        story = CURATED_STORIES[0]  # По умолчанию первый хит

    out_dir = Path(args.out)
    clean_name = f"cinematic_{story.category}_{int(Path().stat().st_mtime)}.mp4" if Path().exists() else "master_cinematic.mp4"
    final_video = assemble_cinematic_video(
        story,
        out_dir=out_dir,
        out_filename=clean_name,
        upscale_4k=args.enable_4k,
    )

    print("\n🎉 ГОТОВО К ПУБЛИКАЦИИ В TIKTOK / SHORTS / REELS:")
    print(f"   Видео: file:///{final_video.resolve().as_posix()}")

    if args.open:
        try:
            os.startfile(str(final_video))
        except Exception:
            pass


if __name__ == "__main__":
    main()

