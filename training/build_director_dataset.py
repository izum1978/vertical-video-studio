"""Сборка датасета режиссёра ИЗ ВАШЕГО ЖЕ ПАЙПЛАЙНА.

Запрос в обучении собирается той же функцией build_user_prompt и с тем же системным
промптом, что и в боевом director_llm.py. Поэтому обучение совпадает с использованием.

Вход:  topics.txt, строки вида  жанр|тема   (например: horror_rules|Правила ночной смены на складе)
Выход: data/director_train.jsonl, data/director_val.jsonl, data/director_rejected.jsonl

Запуск (из корня проекта):
  python training/build_director_dataset.py --topics training/topics.txt \
      --script-provider claude --director-provider claude --tts edge
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.director_llm import (  # noqa: E402
    DIRECTOR_SYSTEM_PROMPT, STORYBOARD_SCHEMA, build_user_prompt, check_storyboard,
    parse_json_loose, split_sentences_with_timing,
)
from app.scene_resolver import HORROR_SCENES, normalize_scene_type  # noqa: E402

BEAT_FIELDS = ["id", "start", "end", "text", "mode", "scene_type", "title", "subtitle",
               "camera_shot", "camera_motion"]
OPTIONAL_FIELDS = ["items", "overlays", "visual"]   # сцены-списки и оверлеи движка motion_gfx
WORDS_PER_SECOND = 2.6


def quality_errors(beats: list[dict], preset: str) -> list[str]:
    """Фильтр качества СВЕРХ базовой проверки: плохие примеры в датасет не попадают."""
    errs = []
    if not 4 <= len(beats) <= 14:
        errs.append(f"число битов {len(beats)} вне диапазона 4-14")
    for b in beats:
        d = b["end"] - b["start"]
        if not 1.5 <= d <= 6.0:
            errs.append(f"бит {b['id']}: длительность {d:.1f} с")
        if len(str(b.get("title", "")).split()) > 3:
            errs.append(f"бит {b['id']}: title длиннее 3 слов")
        if not b.get("camera_shot") or not b.get("camera_motion"):
            errs.append(f"бит {b['id']}: нет camera_shot/camera_motion")
    types = [b["scene_type"] for b in beats if b["mode"] == "motion"]
    if len(beats) >= 6 and len(set(types)) < 3:
        errs.append("слишком мало разных scene_type")
    if preset == "horror_rules":
        share = len(types) / max(1, len(beats))
        if share < 0.8:
            errs.append(f"для horror_rules motion {share:.0%} (< 80%)")
        if any(t not in HORROR_SCENES for t in types):
            errs.append("в horror_rules попала не хоррор-сцена")
    return errs


def canonical_beats(parsed: dict, total: float) -> list[dict]:
    """Оставляем только поля схемы, нормализуем scene_type, склеиваем границы."""
    beats = []
    for i, b in enumerate(parsed["beats"]):
        row = {k: b.get(k) for k in BEAT_FIELDS}
        row["id"] = i + 1
        for k in OPTIONAL_FIELDS:
            if b.get(k):
                row[k] = b[k]
        row["scene_type"] = normalize_scene_type(b.get("scene_type")) or ""
        row["start"], row["end"] = round(float(b["start"]), 2), round(float(b["end"]), 2)
        beats.append(row)
    beats[0]["start"], beats[-1]["end"] = 0.0, round(total, 2)
    for a, b in zip(beats, beats[1:]):
        b["start"] = a["end"]
    return beats


def split_of(key: str, val_share: float = 0.1) -> str:
    """Разделение train/val по ТЕМЕ (хэш), чтобы одна тема не попала в обе выборки."""
    h = int(hashlib.md5(key.encode("utf-8")).hexdigest(), 16) % 1000
    return "val" if h < val_share * 1000 else "train"


def build_record(topic, preset, script_fn, timing_fn, llm, max_attempts=3):
    """script_fn(topic, preset) -> dict(script,title); timing_fn(script_text) -> (words|None, total);
    llm(system, user) -> raw json str. Возвращает (record|None, причина_отказа|None)."""
    sc = script_fn(topic, preset)
    words, total = timing_fn(sc["script"])
    sents = split_sentences_with_timing(sc["script"], words, total)
    user = build_user_prompt(sc.get("title") or topic, preset, total, sents)
    feedback, last = "", []
    for _ in range(max_attempts):
        try:
            parsed = parse_json_loose(llm(DIRECTOR_SYSTEM_PROMPT, user + feedback))
        except Exception as e:  # noqa: BLE001
            last = [f"ответ не JSON: {e}"]
            continue
        errs = check_storyboard(parsed, total)
        if not errs:
            beats = canonical_beats(parsed, total)
            errs = quality_errors(beats, preset)
            if not errs:
                answer = json.dumps({"beats": beats}, ensure_ascii=False)
                return {"messages": [{"role": "system", "content": DIRECTOR_SYSTEM_PROMPT},
                                     {"role": "user", "content": user},
                                     {"role": "assistant", "content": answer}],
                        "meta": {"topic": topic, "preset": preset, "duration": total,
                                 "split": split_of(topic)}}, None
        last = errs
        feedback = "\n\nПредыдущий ответ не подошёл: " + "; ".join(errs[:5]) + ". Исправь и верни полный JSON."
    return None, "; ".join(last)


def estimate_timing(script_text):
    """Быстрый режим без TTS: слова размазываются по времени с постоянным темпом."""
    from app.director_llm import clean_for_tts
    n = max(1, len(clean_for_tts(script_text).split()))
    return None, round(n / WORDS_PER_SECOND, 2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--topics", required=True)
    ap.add_argument("--out", default=str(ROOT / "training" / "data"))
    ap.add_argument("--script-provider", default="claude")
    ap.add_argument("--director-provider", default="claude")
    ap.add_argument("--tts", choices=["edge", "estimate"], default="edge")
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()

    from app import providers as P
    from app.director_llm import call_llm
    from app.render import probe_duration

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    files = {"train": out / "director_train.jsonl", "val": out / "director_val.jsonl",
             "rejected": out / "director_rejected.jsonl"}
    done = set()
    for f in files.values():  # докачка: уже обработанные темы пропускаем
        if f.exists():
            for line in f.read_text(encoding="utf-8").splitlines():
                try:
                    m = json.loads(line).get("meta", {})
                    done.add((m.get("preset"), m.get("topic")))
                except json.JSONDecodeError:
                    pass
    script_prov = P.get(P.SCRIPTS, a.script_provider)
    tts_prov = P.get(P.TTS, "edge") if a.tts == "edge" else None
    work = ROOT / "work" / "dataset"
    work.mkdir(parents=True, exist_ok=True)

    def script_fn(topic, preset):
        return script_prov.generate(topic, preset, "ru")

    def timing_fn(script_text):
        if tts_prov is None:
            return estimate_timing(script_text)
        clean = re.sub(r"[*!]", "", re.sub(r"\[sfx:\s*\w+\]", "", script_text, flags=re.I))
        key = hashlib.md5(clean.encode()).hexdigest()[:10]
        audio = tts_prov.synth(clean, "", "ru", work / f"{key}.mp3")
        wf = work / f"{key}.words.json"
        src = Path(str(audio)).with_suffix(".words.json")
        words = json.loads(src.read_text(encoding="utf-8")) if src.exists() else (
            json.loads(wf.read_text(encoding="utf-8")) if wf.exists() else None)
        return words, probe_duration(audio)

    def llm(system, user):
        return call_llm(a.director_provider, system, user, STORYBOARD_SCHEMA)[0]

    topics = [l.strip().split("|", 1) for l in Path(a.topics).read_text(encoding="utf-8").splitlines()
              if "|" in l and not l.startswith("#")]
    ok = bad = 0
    for preset, topic in topics[: a.limit or None]:
        preset, topic = preset.strip(), topic.strip()
        if (preset, topic) in done:
            continue
        try:
            rec, why = build_record(topic, preset, script_fn, timing_fn, llm)
        except Exception as e:  # noqa: BLE001
            rec, why = None, f"{type(e).__name__}: {e}"
        target = files[rec["meta"]["split"]] if rec else files["rejected"]
        row = rec or {"meta": {"topic": topic, "preset": preset, "reason": why}}
        with target.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        ok, bad = ok + bool(rec), bad + (not rec)
        print(f"[{ok} ok / {bad} отбраковано] {preset}: {topic[:60]}", flush=True)


if __name__ == "__main__":
    main()
