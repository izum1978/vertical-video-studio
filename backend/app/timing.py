"""Таймкоды слов: реальные границы от edge-tts, запасной вариант с паузами на знаках препинания."""


def marks_to_words(marks: list[dict]) -> list[dict]:
    """marks: события edge-tts [{word,start,end,kind}] (kind: WordBoundary | SentenceBoundary).
    Границы предложений реальные; внутри предложения слова делятся по длине."""
    words = []
    for m in marks:
        if m.get("kind") == "SentenceBoundary":
            ws = str(m["word"]).split()
            if not ws:
                continue
            weights = [len(w) + 2 for w in ws]
            t, span = m["start"], m["end"] - m["start"]
            for w, wt in zip(ws, weights):
                d = span * wt / sum(weights)
                words.append({"word": w, "start": round(t, 3), "end": round(t + d, 3)})
                t += d
        else:
            words.append({"word": m["word"], "start": m["start"], "end": m["end"]})
    return words


def proportional_timing(text: str, duration: float) -> list[dict]:
    """Запасной вариант без событий: вес слова = длина + пауза после знака препинания."""
    words = text.split()
    if not words or duration <= 0:
        return []

    def weight(w):
        extra = 6 if w.endswith((".", "?", "!", "…")) else 3 if w.endswith((",", ";", ":", "-")) else 0
        return len(w.strip(".,;:!?…-")) + 2 + extra

    weights = [weight(w) for w in words]
    total, t, out = sum(weights), 0.0, []
    for w, wt in zip(words, weights):
        d = duration * wt / total
        out.append({"word": w, "start": round(t, 3), "end": round(t + d, 3)})
        t += d
    return out


def _norm(w: str) -> str:
    import re
    return re.sub(r"[^\w]", "", str(w), flags=re.UNICODE).lower()


def restore_punctuation(words: list[dict], text: str) -> list[dict]:
    """События озвучки отдают слова без знаков препинания, а субтитры рвут фразы по запятым и точкам.
    Подставляет слова из исходного текста (с пунктуацией), сохраняя реальные времена."""
    tokens = str(text).split()
    out, j = [], 0
    for w in words:
        n = _norm(w.get("word", ""))
        k = None
        if n:
            for look in range(j, min(len(tokens), j + 4)):     # допускаем до 3 пропущенных токенов (тире и т. п.)
                if _norm(tokens[look]) == n:
                    k = look
                    break
        if k is not None:
            out.append({**w, "word": tokens[k]})
            j = k + 1
        else:
            out.append(dict(w))
    return out


def alignment_to_words(alignment) -> list[dict]:
    """Посимвольное выравнивание ElevenLabs (with-timestamps) -> слова с временами."""
    try:
        chars = alignment["characters"]
        starts = alignment["character_start_times_seconds"]
        ends = alignment["character_end_times_seconds"]
    except (TypeError, KeyError):
        return []
    if not (len(chars) == len(starts) == len(ends)):
        return []
    words, cur, t0, t1 = [], "", None, None
    for ch, s, e in zip(chars, starts, ends):
        if str(ch).isspace():
            if cur:
                words.append({"word": cur, "start": round(float(t0), 3), "end": round(float(t1), 3)})
            cur, t0, t1 = "", None, None
            continue
        if t0 is None:
            t0 = s
        cur += str(ch)
        t1 = e
    if cur:
        words.append({"word": cur, "start": round(float(t0), 3), "end": round(float(t1), 3)})
    return words
