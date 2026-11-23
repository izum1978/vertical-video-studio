"""Модуль генерации кинематографичных субтитров (100% бесплатно через ASS + libass).

Создаёт динамичные субтитры в стиле вирусных TikTok/Shorts:
- Крупный жирный шрифт в безопасной зоне 9:16
- Короткие фразы (2-3 слова на экране)
- Пословная золотистая подсветка активного слова по точным таймкодам Microsoft TTS
- Чёткий контрастный контур и мягкая тень
"""
from pathlib import Path
from typing import Dict, List, Optional


def format_ass_time(seconds: float) -> str:
    """Форматирует секунды в стандартный ASS таймкод: H:MM:SS.cs"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    cs = int(round((seconds - int(seconds)) * 100))
    if cs >= 100:
        cs = 99
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def generate_cinematic_ass(
    words: List[Dict],
    out_path: Path,
    words_per_phrase: int = 3,
    font_name: str = "Arial",
    font_size: int = 68,
    primary_color: str = "&H00FFFFFF",      # Белый
    highlight_color: str = "&H002BF5FF",    # Неоново-золотой/янтарный (BGR: &H00 + BB + GG + RR)
    outline_color: str = "&H00050505",      # Почти чёрный глубокий контур
    margin_v: int = 420,                    # Отступ снизу для безопасной зоны 9:16
) -> Path:
    """Генерирует профессиональный .ass файл с динамической пословной подсветкой."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    header = f"""[Script Info]
Title: Cinematic Viral Subtitles
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{font_name},{font_size},{primary_color},&H000000FF,{outline_color},&H80000000,-1,0,0,0,100,100,1.5,0,1,5.5,2.0,2,60,60,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    if not words:
        out_path.write_text(header, encoding="utf-8")
        return out_path

    # Разбиваем слова на компактные фразы по 2-4 слова
    chunks = []
    current_chunk = []
    for w in words:
        current_chunk.append(w)
        # Разделяем по длине или знакам препинания
        if len(current_chunk) >= words_per_phrase or any(w["word"].endswith(p) for p in [".", "!", "?", "...", ","]):
            chunks.append(current_chunk)
            current_chunk = []
    if current_chunk:
        chunks.append(current_chunk)

    dialogue_lines = []
    for chunk in chunks:
        chunk_start = chunk[0]["start"]
        chunk_end = chunk[-1]["end"]

        # Для каждого слова внутри чанка генерируем отдельный субкадр с подсветкой
        for idx, active_word in enumerate(chunk):
            word_start = active_word["start"]
            word_end = active_word["end"]
            if word_end <= word_start:
                word_end = word_start + 0.15

            # Собираем строку фразы с подсветкой активного слова
            text_parts = []
            for j, w in enumerate(chunk):
                raw_text = w["word"].upper()
                if j == idx:
                    # Подсвеченное слово: цвет + лёгкое увеличение
                    text_parts.append(r"{\c" + highlight_color + r"\fscx108\fscy108}" + raw_text + r"{\r}")
                else:
                    # Обычное белое слово
                    text_parts.append(r"{\c" + primary_color + r"}" + raw_text)

            line_text = " ".join(text_parts)
            dialogue_lines.append(
                f"Dialogue: 0,{format_ass_time(word_start)},{format_ass_time(word_end)},Default,,0,0,0,,{line_text}"
            )

    full_ass_content = header + "\n".join(dialogue_lines) + "\n"
    out_path.write_text(full_ass_content, encoding="utf-8")
    return out_path


if __name__ == "__main__":
    import json
    test_words_file = Path("output/test_voice/words.json")
    if test_words_file.exists():
        words = json.loads(test_words_file.read_text(encoding="utf-8"))
        out_ass = Path("output/test_voice/subtitles.ass")
        generate_cinematic_ass(words, out_ass)
        print(f"Субтитры успешно созданы: {out_ass}")

