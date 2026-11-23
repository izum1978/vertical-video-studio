import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.timing import marks_to_words, proportional_timing


def test_sentence_marks_keep_real_pause():
    marks = [{"word": "Привет мир", "start": 0.0, "end": 1.0, "kind": "SentenceBoundary"},
             {"word": "Снова тишина", "start": 2.0, "end": 3.5, "kind": "SentenceBoundary"}]
    w = marks_to_words(marks)
    assert [x["word"] for x in w] == ["Привет", "мир", "Снова", "тишина"]
    assert w[1]["end"] == 1.0 and w[2]["start"] == 2.0          # пауза 1 с сохранена
    assert abs(w[-1]["end"] - 3.5) < 0.01


def test_word_marks_pass_through():
    w = marks_to_words([{"word": "да", "start": 0.1, "end": 0.3, "kind": "WordBoundary"}])
    assert w == [{"word": "да", "start": 0.1, "end": 0.3}]


def test_proportional_covers_duration_and_pauses_longer():
    w = proportional_timing("Свет погас. Он ждал, молча.", 10.0)
    assert abs(w[-1]["end"] - 10.0) < 0.01 and w[0]["start"] == 0.0
    plain = proportional_timing("Свет погас Он ждал молча", 10.0)
    assert (w[1]["end"] - w[1]["start"]) > (plain[1]["end"] - plain[1]["start"])  # слово перед точкой длиннее
    assert proportional_timing("", 5) == [] and proportional_timing("а", 0) == []


def test_restore_punctuation_keeps_real_times_and_survives_mismatch():
    from app.timing import restore_punctuation
    ev = [{"word": "Привет", "start": 0.0, "end": 0.4}, {"word": "мир", "start": 0.5, "end": 0.8},
          {"word": "как", "start": 1.0, "end": 1.2}, {"word": "дела", "start": 1.2, "end": 1.6}]
    out = restore_punctuation(ev, "Привет, мир - как дела?")
    assert [w["word"] for w in out] == ["Привет,", "мир", "как", "дела?"]       # тире между словами пропущено
    assert [w["start"] for w in out] == [0.0, 0.5, 1.0, 1.2]
    odd = restore_punctuation([{"word": "иное", "start": 0, "end": 1}], "совсем другой текст")
    assert odd == [{"word": "иное", "start": 0, "end": 1}]                       # не совпало: слово не трогаем


def test_elevenlabs_alignment_becomes_words_with_punctuation():
    from app.timing import alignment_to_words
    al = {"characters": list("Да, нет."), "character_start_times_seconds": [0, .1, .2, .3, .4, .5, .6, .7],
          "character_end_times_seconds": [.1, .2, .3, .4, .5, .6, .7, .8]}
    assert alignment_to_words(al) == [{"word": "Да,", "start": 0.0, "end": 0.3}, {"word": "нет.", "start": 0.4, "end": 0.8}]
    assert alignment_to_words(None) == [] and alignment_to_words({"characters": ["а"]}) == []
