"""Таймкоды озвучки: Edge (события границ), ElevenLabs (выравнивание), OpenAI (оценка с паузами). Сеть подменена."""
import asyncio
import base64
import json
import os
import subprocess
import sys
import tempfile
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.providers import tts  # noqa: E402

TEXT = "Привет, мир! Как дела? Всё хорошо."


def _mp3(path: Path, seconds=3.0):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"sine=frequency=220:duration={seconds}",
                    "-c:a", "libmp3lame", "-b:a", "96k", str(path)], check=True)
    return path.read_bytes()


def _install_fake_edge(audio: bytes, events, accept_boundary=True):
    seen = {}

    class Communicate:
        def __init__(self, text, voice, **kw):
            if kw and not accept_boundary:
                raise TypeError("старая версия: boundary не поддерживается")
            seen["kw"] = kw
            seen["text"] = text

        async def stream(self):
            half = len(audio) // 2
            yield {"type": "audio", "data": audio[:half]}
            for ev in events:
                yield ev
            yield {"type": "audio", "data": audio[half:]}

    mod = types.ModuleType("edge_tts")
    mod.Communicate = Communicate
    sys.modules["edge_tts"] = mod
    return seen


def _words_file(out: Path):
    return json.loads(out.with_suffix(".words.json").read_text(encoding="utf-8"))


def test_edge_word_events_get_real_times_and_script_punctuation():
    with tempfile.TemporaryDirectory() as d:
        audio = _mp3(Path(d) / "src.mp3")
        ev = [{"type": "WordBoundary", "offset": int(t * 1e7), "duration": int(0.3 * 1e7), "text": w}
              for t, w in [(0.2, "Привет"), (0.7, "мир"), (1.4, "Как"), (1.8, "дела"), (2.3, "Всё"), (2.6, "хорошо")]]
        seen = _install_fake_edge(audio, ev)
        out = Path(d) / "v.mp3"
        tts.EdgeTTS().synth(TEXT, "ru-RU-SvetlanaNeural", "ru", out)
        words = _words_file(out)
    assert seen["kw"] == {"boundary": "WordBoundary"}
    assert [w["word"] for w in words] == ["Привет,", "мир", "Как", "дела?", "Всё", "хорошо."]       # «!» вырезается очисткой текста (разметка акцентов)
    assert [w["start"] for w in words] == [0.2, 0.7, 1.4, 1.8, 2.3, 2.6]       # времена из событий, а не оценка


def test_edge_sentence_events_keep_real_pauses_between_sentences():
    with tempfile.TemporaryDirectory() as d:
        audio = _mp3(Path(d) / "src.mp3")
        ev = [{"type": "SentenceBoundary", "offset": int(a * 1e7), "duration": int((b - a) * 1e7), "text": t}
              for a, b, t in [(0.1, 0.9, "Привет, мир!"), (1.6, 2.2, "Как дела?"), (2.7, 3.0, "Всё хорошо.")]]
        _install_fake_edge(audio, ev)
        out = Path(d) / "v.mp3"
        tts.EdgeTTS().synth(TEXT, "ru-RU-SvetlanaNeural", "ru", out)
        words = _words_file(out)
    assert words[2]["start"] == 1.6 and words[0]["start"] == 0.1 and words[1]["end"] == 0.9    # пауза 0,7 с сохранена
    assert words[0]["word"] == "Привет," and words[-1]["word"] == "хорошо."


def test_edge_works_with_old_library_without_boundary_parameter():
    with tempfile.TemporaryDirectory() as d:
        audio = _mp3(Path(d) / "src.mp3")
        seen = _install_fake_edge(audio, [], accept_boundary=False)
        out = Path(d) / "v.mp3"
        tts.EdgeTTS().synth(TEXT, "ru-RU-SvetlanaNeural", "ru", out)
        words = _words_file(out)                     # событий нет: оценка с паузами, но файл есть
    assert seen["kw"] == {} and len(words) == 6 and words[-1]["end"] > 2.5


class _Resp:
    def __init__(self, content=b"", data=None, fail=False):
        self.content, self._data, self._fail = content, data, fail

    def raise_for_status(self):
        if self._fail:
            raise RuntimeError("HTTP 404")

    def json(self):
        return self._data


def test_elevenlabs_uses_alignment_and_falls_back_to_plain_synthesis():
    os.environ["ELEVENLABS_API_KEY"] = "test-key"
    import app.config as cfg
    orig_post = tts.httpx.post
    try:
        with tempfile.TemporaryDirectory() as d:
            audio = _mp3(Path(d) / "src.mp3")
            chars = list("Да, нет.")
            al = {"characters": chars, "character_start_times_seconds": [i * 0.1 for i in range(len(chars))],
                  "character_end_times_seconds": [i * 0.1 + 0.1 for i in range(len(chars))]}
            tts.httpx.post = lambda url, **kw: _Resp(data={"audio_base64": base64.b64encode(audio).decode(), "alignment": al})
            out = Path(d) / "a.mp3"
            tts.ElevenLabsTTS().synth("Да, нет.", "", "ru", out)
            words = _words_file(out)
            assert [w["word"] for w in words] == ["Да,", "нет."] and words[1]["start"] == 0.4
            calls = []

            def flaky(url, **kw):
                calls.append(url)
                return _Resp(fail=True) if url.endswith("with-timestamps") else _Resp(content=audio)
            tts.httpx.post = flaky
            out2 = Path(d) / "b.mp3"
            tts.ElevenLabsTTS().synth("Да, нет.", "", "ru", out2)
            assert len(calls) == 2 and calls[0].endswith("with-timestamps") and not calls[1].endswith("with-timestamps")
            assert len(_words_file(out2)) == 2         # запасной путь: оценка с паузами
    finally:
        tts.httpx.post = orig_post
        os.environ.pop("ELEVENLABS_API_KEY", None)


def test_openai_estimate_puts_longer_time_before_sentence_end():
    os.environ["OPENAI_API_KEY"] = "test-key"
    orig_post = tts.httpx.post
    try:
        with tempfile.TemporaryDirectory() as d:
            audio = _mp3(Path(d) / "src.mp3", 4.0)
            tts.httpx.post = lambda url, **kw: _Resp(content=audio)
            out = Path(d) / "o.mp3"
            tts.OpenAITTS().synth("Свет погас. Он ждал, молча.", "onyx", "ru", out)
            w = _words_file(out)
    finally:
        tts.httpx.post = orig_post
        os.environ.pop("OPENAI_API_KEY", None)
    assert abs(w[-1]["end"] - 4.0) < 0.1 and w[0]["start"] == 0.0
    assert (w[1]["end"] - w[1]["start"]) > (w[0]["end"] - w[0]["start"]) * 0.8      # слово перед точкой не короче
