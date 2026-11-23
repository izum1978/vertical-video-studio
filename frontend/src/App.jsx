import { useEffect, useRef, useState } from "react";

// --- SVG Icons (no external package dependency needed) ---
const Icons = {
  Sparkles: () => (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.286L13 21l-2.286-6.857L5 12l5.714-2.286L13 3z" />
    </svg>
  ),
  Play: () => (
    <svg className="w-4 h-4 fill-current" viewBox="0 0 24 24">
      <path d="M8 5v14l11-7z" />
    </svg>
  ),
  Download: () => (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
    </svg>
  ),
  Trash: () => (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
    </svg>
  ),
  Copy: () => (
    <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
    </svg>
  ),
  Check: () => (
    <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
    </svg>
  ),
  Terminal: () => (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
    </svg>
  ),
  Video: () => (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
    </svg>
  ),
  Refresh: () => (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
    </svg>
  ),
  Film: () => (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z" />
    </svg>
  ),
  Layers: () => (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
    </svg>
  ),
};

const QUICK_TOPICS = [
  "Правила выживания на даче, если ровно в полночь пропала связь",
  "Инструкция жильцам 9-этажки, если лифт поехал на 13-й этаж",
  "Что делать, если в лесу ночью вас зовут по имени знакомым голосом",
  "Что скрывали архивы Ватикана о конце света",
  "Секретный эксперимент 1968 года, который засекретили",
  "3 бесплатные нейросети, заменяющие целую студию дизайна",
  "5 гениальных находок для дома до 1000 рублей",
];

const QUICK_BATCH_PACKS = [
  {
    name: "👁️ Сезон хоррор-правил (Аналоговый хоррор)",
    preset: "horror_rules",
    sub_style: "ref",
    cta: "Вторая часть и секретные протоколы выживания по ссылке в шапке профиля 👆",
    topics: [
      "Правила выживания на даче, если ровно в полночь пропала связь",
      "Инструкция жильцам 9-этажки, если лифт поехал на 13-й этаж",
      "Что делать, если в лесу ночью вас зовут по имени знакомым голосом",
      "Свод правил для ночного сторожа в заброшенном пионерлагере",
      "Инструкция при аномальном ночном тумане: никогда не открывайте двери",
    ],
  },
  {
    name: "🚀 УБТ в Telegram (Тайны)",
    preset: "tg_cliffhanger",
    sub_style: "mrbeast",
    cta: "Секретные материалы и развязка по ссылке в шапке профиля 👆",
    topics: [
      "Что скрывали архивы Ватикана о конце света",
      "Секретный эксперимент 1968 года, который засекретили",
      "Почему в Японии запрещено фотографировать в метро",
      "Реальная причина, почему пропала Янтарная комната",
      "Что на самом деле нашли на дне Марианской впадины",
    ],
  },
  {
    name: "💻 IT & Секретные нейросети",
    preset: "it",
    sub_style: "neon",
    cta: "Бесплатный список этих нейросетей закреплен в Telegram в шапке 🚀",
    topics: [
      "3 бесплатные нейросети, заменяющие целую студию дизайна",
      "Как создать приложение без кода за 15 минут",
      "Скрытая функция Telegram, о которой знают единицы",
      "Нейросеть, которая делает монтаж видео на автомате",
      "Как автоматизировать рутину на компьютере за 3 клика",
    ],
  },
  {
    name: "🛍️ Товарка / E-commerce",
    preset: "ecommerce",
    sub_style: "clean",
    cta: "Артикулы и прямые ссылки на скидки в шапке профиля 🛒",
    topics: [
      "5 гениальных находок для дома до 1000 рублей",
      "Гаджет, который спасает осанку при работе за ноутбуком",
      "Умная термокружка с датчиком температуры: стоит ли брать",
      "Беспроводной пылесос для авто, который тянет всё",
      "Топ-3 полезных девайса для кухни в 2026 году",
    ],
  },
];

const STAGE_ICONS = ["✍️", "🎙️", "🎬", "⚙️", "✅"];

const PRESET_CARDS = [
  { id: "horror_rules", icon: "👁️", title: "Хоррор", sub: "Свод правил" },
  { id: "tg_cliffhanger", icon: "🚀", title: "УБТ в TG", sub: "Клиффхэнгер" },
  { id: "facts", icon: "💡", title: "Факты", sub: "Интрига" },
  { id: "ecommerce", icon: "🛍️", title: "Товарка", sub: "WB / Ozon" },
  { id: "motivation", icon: "🔥", title: "Мотив", sub: "Драйв" },
  { id: "it", icon: "💻", title: "IT/Tech", sub: "Обучение" },
];

export default function App() {
  const [mode, setMode] = useState("batch"); // "single" | "batch"
  const [opts, setOpts] = useState(null);
  const [form, setForm] = useState({
    topic: "",
    preset: "horror_rules",
    lang: "ru",
    voice: "",
    script: "qwen",
    tts: "edge",
    visuals: "motion_gfx",
    scene_gen: "auto",
    sub_style: "ref",
    cta: "Вторая часть и секретные протоколы в шапке профиля 👆",
    mock: false,
  });

  const [batchTopicsText, setBatchTopicsText] = useState(
    "Что скрывали архивы Ватикана о конце света\nСекретный эксперимент 1968 года, который засекретили\nПочему в Японии запрещено фотографировать в метро\nРеальная причина, почему пропала Янтарная комната\nЧто на самом деле нашли на дне Марианской впадины"
  );
  const [batchJob, setBatchJob] = useState(null);
  const [batchProgress, setBatchProgress] = useState(null);

  const [job, setJob] = useState(null);
  const [videos, setVideos] = useState([]);
  const [current, setCurrent] = useState(null);
  const [err, setErr] = useState("");
  const [backendOnline, setBackendOnline] = useState(false);
  const [copiedKey, setCopiedKey] = useState(null);
  const [elapsedSec, setElapsedSec] = useState(0);

  const logRef = useRef(null);
  const timerRef = useRef(null);
  const videoPlayerRef = useRef(null);

  const setField = (key) => (val) => setForm((prev) => ({ ...prev, [key]: val }));

  const loadVideos = async () => {
    try {
      const res = await fetch("/api/videos");
      if (res.ok) {
        const data = await res.json();
        setVideos(data);
        if (data.length > 0 && !current) {
          setCurrent(data[0]);
        }
      }
    } catch {
      // offline or failing
    }
  };

  const checkConnection = async () => {
    try {
      const res = await fetch("/api/options");
      if (res.ok) {
        const data = await res.json();
        setOpts(data);
        setBackendOnline(true);
        setErr("");
        loadVideos();
      } else {
        setBackendOnline(false);
      }
    } catch {
      setBackendOnline(false);
    }
  };

  useEffect(() => {
    checkConnection();
    const interval = setInterval(() => {
      if (!backendOnline) checkConnection();
    }, 5000);
    return () => clearInterval(interval);
  }, [backendOnline]);

  // Auto-scroll logs
  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
  }, [job?.logs?.length]);

  // Elapsed timer when job is running
  useEffect(() => {
    const isAct = job?.status === "running" || batchJob?.status === "running";
    if (isAct) {
      setElapsedSec(0);
      timerRef.current = setInterval(() => {
        setElapsedSec((s) => s + 1);
      }, 1000);
    } else {
      if (timerRef.current) clearInterval(timerRef.current);
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [job?.status, batchJob?.status]);

  const copyText = (text, key) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  const deleteVideo = async (id, e) => {
    e.stopPropagation();
    if (!confirm("Удалить этот ролик из библиотеки?")) return;
    try {
      const res = await fetch(`/api/videos/${id}`, { method: "DELETE" });
      if (res.ok) {
        setVideos((prev) => prev.filter((v) => v.id !== id));
        if (current?.id === id) {
          const remain = videos.filter((v) => v.id !== id);
          setCurrent(remain[0] || null);
        }
      }
    } catch {
      alert("Не удалось удалить видео");
    }
  };

  const isRunning = job?.status === "running" || batchJob?.status === "running";

  async function generate(e) {
    e.preventDefault();
    setErr("");

    try {
      const res = await fetch("/api/jobs", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });

      if (!res.ok) {
        let msg = "Не удалось запустить генерацию";
        try {
          const errData = await res.json();
          msg = errData.detail?.toString() || msg;
        } catch {}
        setErr(msg);
        return;
      }

      const newJob = await res.json();
      setJob(newJob);

      // Connect SSE
      const es = new EventSource(`/api/jobs/${newJob.id}/events`);
      es.onmessage = (event) => {
        try {
          const snapshot = JSON.parse(event.data);
          setJob(snapshot);
          if (snapshot.status !== "running") {
            es.close();
            if (snapshot.video) {
              setCurrent(snapshot.video);
            }
            loadVideos();
          }
        } catch (parseErr) {
          console.error("SSE parse error", parseErr);
        }
      };

      es.onerror = () => {
        es.close();
        fetch(`/api/jobs/${newJob.id}`)
          .then((r) => r.json())
          .then((state) => {
            setJob(state);
            if (state.video) setCurrent(state.video);
            loadVideos();
          })
          .catch(() => {});
      };
    } catch (netErr) {
      setErr(`Ошибка сети: ${netErr.message}. Проверьте, запущен ли бэкенд на порту 8000.`);
    }
  }

  async function startBatch(e) {
    e.preventDefault();
    setErr("");

    const topics = batchTopicsText
      .split("\n")
      .map((t) => t.trim())
      .filter(Boolean);

    if (topics.length === 0) {
      setErr("Пожалуйста, введите как минимум одну тему для пакетной генерации");
      return;
    }

    try {
      const payload = {
        ...form,
        topics,
      };

      const res = await fetch("/api/batch", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        let msg = "Не удалось запустить пакетную генерацию";
        try {
          const errData = await res.json();
          msg = errData.detail?.toString() || msg;
        } catch {}
        setErr(msg);
        return;
      }

      const initialBatch = await res.json();
      setBatchJob(initialBatch);
      setBatchProgress(initialBatch);

      const es = new EventSource(`/api/batch/${initialBatch.id}/events`);
      es.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setBatchJob(data.batch);
          setBatchProgress(data.batch);
          if (data.current_job) {
            setJob(data.current_job);
            if (data.current_job.video) {
              setCurrent(data.current_job.video);
            }
          }
          loadVideos();
          if (data.batch.status !== "running") {
            es.close();
            loadVideos();
          }
        } catch (err) {
          console.error("Batch SSE parse err", err);
        }
      };

      es.onerror = () => {
        es.close();
        fetch(`/api/batch/${initialBatch.id}`)
          .then((r) => r.json())
          .then((b) => {
            setBatchJob(b);
            setBatchProgress(b);
            loadVideos();
          })
          .catch(() => {});
      };
    } catch (netErr) {
      setErr(`Ошибка запуска пакета: ${netErr.message}`);
    }
  }

  const applyQuickPack = (pack) => {
    setField("preset")(pack.preset);
    setField("cta")(pack.cta);
    if (pack.sub_style) {
      setField("sub_style")(pack.sub_style);
    }
    setBatchTopicsText(pack.topics.join("\n"));
  };

  const batchTopicsCount = batchTopicsText.split("\n").map((t) => t.trim()).filter(Boolean).length;
  const voices = opts?.voices?.[form.lang] || [];

  return (
    <div className="min-h-screen bg-studio-950 text-slate-100 flex flex-col font-sans">
      {/* --- Top Navbar --- */}
      <header className="border-b border-slate-800/80 bg-studio-900/60 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-cyan-400 p-0.5 shadow-glow flex items-center justify-center">
              <div className="h-full w-full bg-studio-950 rounded-[10px] flex items-center justify-center text-indigo-400">
                <Icons.Sparkles />
              </div>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-extrabold text-base tracking-tight text-white">VERTICAL STUDIO</span>
                <span className="bg-indigo-500/20 text-indigo-300 text-[10px] font-bold px-2 py-0.5 rounded-full border border-indigo-500/30">
                  BATCH AI 60 FPS
                </span>
              </div>
              <p className="text-xs text-slate-400">TikTok, Instagram Reels & Telegram • Пакетная генерация под УБТ</p>
            </div>
          </div>

          {/* Connection status indicator */}
          <div className="flex items-center gap-3">
            <button
              onClick={checkConnection}
              className={`flex items-center gap-2 text-xs px-3 py-1.5 rounded-full border transition-all ${
                backendOnline
                  ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-400"
                  : "bg-rose-500/10 border-rose-500/30 text-rose-400 animate-pulse"
              }`}
              title="Нажмите для повторной проверки связи с бэкендом"
            >
              <span className={`h-2 w-2 rounded-full ${backendOnline ? "bg-emerald-400" : "bg-rose-500"}`} />
              <span>{backendOnline ? "API Online (8000)" : "Бэкенд офлайн"}</span>
              <Icons.Refresh />
            </button>
          </div>
        </div>
      </header>

      {/* --- Backend Offline Warning Banner --- */}
      {!backendOnline && (
        <div className="bg-gradient-to-r from-rose-950/80 via-rose-900/40 to-slate-900 border-b border-rose-500/30 px-4 py-3">
          <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3 text-xs sm:text-sm">
            <div className="flex items-center gap-2 text-rose-200">
              <span className="text-rose-400 font-bold text-base">⚠️</span>
              <span>
                <strong>Бэкенд не обнаружен.</strong> Запустите в терминале:{" "}
                <code className="bg-black/60 px-2 py-0.5 rounded font-mono text-cyan-300 border border-slate-700">
                  uvicorn app.main:app --port 8000
                </code>
              </span>
            </div>
            <button
              onClick={checkConnection}
              className="px-3 py-1 bg-rose-600 hover:bg-rose-500 text-white rounded-lg font-medium transition"
            >
              Проверить снова
            </button>
          </div>
        </div>
      )}

      {/* --- Main 3-Column Studio Workspace --- */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* ================= COLUMN 1: Generator Form (4 cols) ================= */}
        <section className="lg:col-span-4 space-y-4">
          <div className="glass-panel rounded-2xl p-5 shadow-2xl space-y-4 border border-slate-800">
            {/* Mode Switch Tabs */}
            <div className="grid grid-cols-2 gap-1.5 bg-studio-900 p-1.5 rounded-xl border border-slate-800">
              <button
                type="button"
                onClick={() => setMode("batch")}
                className={`py-2 px-3 rounded-lg text-xs font-bold transition flex items-center justify-center gap-2 ${
                  mode === "batch"
                    ? "bg-gradient-to-r from-indigo-600 to-cyan-500 text-white shadow-glow"
                    : "text-slate-400 hover:text-white"
                }`}
              >
                <Icons.Layers />
                <span>Пакетный рендер</span>
                <span className="text-[10px] bg-white/20 text-white px-1.5 py-0.2 rounded-full">Пачка</span>
              </button>

              <button
                type="button"
                onClick={() => setMode("single")}
                className={`py-2 px-3 rounded-lg text-xs font-bold transition flex items-center justify-center gap-2 ${
                  mode === "single"
                    ? "bg-indigo-600 text-white shadow-glow"
                    : "text-slate-400 hover:text-white"
                }`}
              >
                <span>🎯 1 ролик</span>
              </button>
            </div>

            {/* Mode Header */}
            <div className="flex items-center justify-between">
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                {mode === "batch" ? (
                  <>
                    <span className="text-cyan-400">🚀</span> Пакетная генерация (Batch)
                  </>
                ) : (
                  <>
                    <span className="text-indigo-400">✨</span> Одиночное видео
                  </>
                )}
              </h2>
              {form.mock && (
                <span className="text-[11px] font-bold px-2 py-0.5 bg-amber-500/10 text-amber-400 border border-amber-500/30 rounded-md">
                  Mock Mode
                </span>
              )}
            </div>

            {/* Form Container */}
            {mode === "batch" ? (
              <form onSubmit={startBatch} className="space-y-4">
                {/* Batch Topics Textarea */}
                <div>
                  <div className="flex items-center justify-between mb-1.5">
                    <label className="text-xs font-semibold text-slate-300">
                      Список тем (по 1 теме на строку)
                    </label>
                    <span className="text-[10px] font-bold text-cyan-400 bg-cyan-950/60 px-2 py-0.5 rounded border border-cyan-500/30">
                      {batchTopicsCount} видео в очереди
                    </span>
                  </div>
                  <textarea
                    required
                    rows={5}
                    className="field text-xs font-mono leading-relaxed resize-none"
                    value={batchTopicsText}
                    onChange={(e) => setBatchTopicsText(e.target.value)}
                    placeholder="Тема 1&#10;Тема 2&#10;Тема 3..."
                  />

                  {/* Ready Topic Packs */}
                  <div className="mt-2.5">
                    <div className="text-[10px] font-semibold text-slate-400 mb-1.5">
                      Готовые пакеты тем под TikTok / Reels / TG:
                    </div>
                    <div className="grid grid-cols-1 gap-1.5">
                      {QUICK_BATCH_PACKS.map((pack, idx) => (
                        <button
                          key={idx}
                          type="button"
                          onClick={() => applyQuickPack(pack)}
                          className="text-left text-[11px] p-2 rounded-lg bg-studio-850 hover:bg-studio-800 text-slate-300 hover:text-indigo-300 border border-slate-700/60 transition flex items-center justify-between"
                        >
                          <span className="font-medium">{pack.name}</span>
                          <span className="text-[10px] text-slate-500">{pack.topics.length} видео</span>
                        </button>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Preset Selector */}
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                    Направление контента
                  </label>
                  <div className="grid grid-cols-3 gap-1.5">
                    {PRESET_CARDS.map((p) => {
                      const active = form.preset === p.id;
                      return (
                        <button
                          key={p.id}
                          type="button"
                          onClick={() => {
                            setField("preset")(p.id);
                            if (p.id === "horror_rules") {
                              setField("sub_style")("horror");
                              setField("cta")("Вторая часть и секретные протоколы выживания по ссылке в шапке профиля 👆");
                            }
                          }}
                          className={`p-2 rounded-xl text-left border transition-all ${
                            active
                              ? "bg-indigo-600/20 border-indigo-500 text-white shadow-glow"
                              : "bg-studio-850/60 border-slate-800 text-slate-400 hover:border-slate-700 hover:text-slate-200"
                          }`}
                        >
                          <div className="text-sm mb-0.5">{p.icon}</div>
                          <div className="text-[11px] font-bold leading-tight truncate">{p.title}</div>
                          <div className="text-[9px] text-slate-400 truncate">{p.sub}</div>
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* Subtitle Styles Selector */}
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                    Стиль субтитров (60 FPS ASS)
                  </label>
                  <div className="grid grid-cols-2 gap-1.5">
                    {[
                      { id: "ref", label: "🎯 Как в референсе (по словам)" },
                      { id: "mrbeast", label: "🟡 MrBeast Жёлтый" },
                      { id: "neon", label: "💎 Неоновый Циан" },
                      { id: "clean", label: "⚪ Чистый Белый" },
                      { id: "gold", label: "👑 Luxury Золото" },
                    ].map((s) => (
                      <button
                        key={s.id}
                        type="button"
                        onClick={() => setField("sub_style")(s.id)}
                        className={`p-2 rounded-xl text-xs font-bold border transition text-left ${
                          form.sub_style === s.id
                            ? "bg-indigo-600/30 border-indigo-500 text-white shadow-glow"
                            : "bg-studio-850/60 border-slate-800 text-slate-400 hover:text-slate-200"
                        }`}
                      >
                        {s.label}
                      </button>
                    ))}
                  </div>
                </div>

                {/* AI Script Provider */}
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    AI-генератор сценария
                  </label>
                  <div className="grid grid-cols-2 gap-1.5">
                    {[
                      { id: "qwen", label: "🦙 Qwen Local" },
                      { id: "gemini", label: "✨ Gemini (Беспл.)" },
                    ].map((m) => (
                      <button
                        key={m.id}
                        type="button"
                        onClick={() => setField("script")(m.id)}
                        className={`p-1.5 rounded-lg text-xs font-semibold border transition text-center ${
                          form.script === m.id
                            ? "bg-indigo-600/30 border-indigo-500 text-white shadow-glow"
                            : "bg-studio-850/60 border-slate-800 text-slate-400 hover:text-slate-200"
                        }`}
                      >
                        {m.label}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Visuals Provider */}
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Генератор видеоряда
                  </label>
                  <div className="grid grid-cols-2 gap-1.5">
                    {[
                      { id: "motion_gfx", label: "🎞️ Motion graphics (стиль референса, без GPU)" },
                      { id: "ai_video", label: "🎬 AI Видеодиффузия (SVD-XT на GPU)" },
                      { id: "ai_scenes", label: "⚡ Быстрый AI-кадр (Ken Burns 60 FPS)" },
                      { id: "kling", label: "🌐 Облачные видеосети (Kling / Runway)" },
                    ].map((v) => (
                      <button
                        key={v.id}
                        type="button"
                        onClick={() => setField("visuals")(v.id)}
                        className={`p-1.5 rounded-lg text-[11px] font-semibold border transition text-center ${
                          form.visuals === v.id
                            ? "bg-indigo-600/30 border-indigo-500 text-white shadow-glow"
                            : "bg-studio-850/60 border-slate-800 text-slate-400 hover:text-slate-200"
                        }`}
                      >
                        {v.label}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Scene designer */}
                {form.visuals === "motion_gfx" && (
                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1">
                      Художник сцен (рисует новую сцену под фразу)
                    </label>
                    <div className="grid grid-cols-2 gap-1.5">
                      {[
                        { id: "auto", label: "🎨 Авто: нужные биты, LLM + словарь" },
                        { id: "all", label: "🖌️ Все биты рисуем заново" },
                        { id: "heuristic", label: "⚡ Быстро: по словарю, без LLM" },
                        { id: "off", label: "📦 Только готовые сцены" },
                      ].map((v) => (
                        <button
                          key={v.id}
                          type="button"
                          onClick={() => setField("scene_gen")(v.id)}
                          className={`p-1.5 rounded-lg text-[11px] font-semibold border transition text-center ${
                            form.scene_gen === v.id
                              ? "bg-indigo-600/30 border-indigo-500 text-white shadow-glow"
                              : "bg-studio-850/60 border-slate-800 text-slate-400 hover:text-slate-200"
                          }`}
                        >
                          {v.label}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* Language & Voice */}
                <div className="grid grid-cols-2 gap-2.5">
                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1">Язык</label>
                    <select
                      className="field text-xs"
                      value={form.lang}
                      onChange={(e) => setForm((prev) => ({ ...prev, lang: e.target.value, voice: "" }))}
                    >
                      <option value="ru">🇷🇺 Русский</option>
                      <option value="en">🇺🇸 English</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1">Голос</label>
                    <select
                      className="field text-xs"
                      value={form.voice}
                      onChange={(e) => setField("voice")(e.target.value)}
                    >
                      <option value="">По умолчанию</option>
                      {voices.map((v) => (
                        <option key={v.id} value={v.id}>
                          {v.label}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                {/* Mock Mode Switch */}
                <label className="flex items-start gap-2.5 p-2.5 rounded-xl bg-studio-850/60 border border-slate-800 cursor-pointer hover:border-slate-700 transition">
                  <input
                    type="checkbox"
                    className="mt-0.5 h-4 w-4 rounded border-slate-700 bg-studio-900 text-indigo-600 focus:ring-indigo-500"
                    checked={form.mock}
                    onChange={(e) => setField("mock")(e.target.checked)}
                  />
                  <div className="text-xs">
                    <span className="font-bold text-slate-200">Mock Mode (Без расхода API)</span>
                    <p className="text-[10px] text-slate-400 mt-0.5">
                      Сборка роликов 60 FPS на тестовых данных без подключения OpenAI/Claude ключей.
                    </p>
                  </div>
                </label>

                {err && (
                  <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-start gap-2">
                    <span>✕</span>
                    <span>{err}</span>
                  </div>
                )}

                <button
                  type="submit"
                  disabled={isRunning || !backendOnline || batchTopicsCount === 0}
                  className={`w-full py-3.5 px-4 rounded-xl font-bold text-sm text-white flex items-center justify-center gap-2 transition-all shadow-glow ${
                    isRunning
                      ? "bg-slate-700 cursor-not-allowed opacity-80"
                      : "bg-gradient-to-r from-indigo-600 via-indigo-500 to-cyan-500 hover:from-indigo-500 hover:to-cyan-400 active:scale-[0.99]"
                  }`}
                >
                  {isRunning ? (
                    <>
                      <span className="animate-spin text-base">⚙️</span>
                      <span>Рендер пачки... ({elapsedSec}s)</span>
                    </>
                  ) : (
                    <>
                      <Icons.Sparkles />
                      <span>Сгенерировать пачку ({batchTopicsCount} видео)</span>
                    </>
                  )}
                </button>
              </form>
            ) : (
              /* Single Video Form */
              <form onSubmit={generate} className="space-y-4">
                <div>
                  <div className="flex items-center justify-between mb-1.5">
                    <label className="text-xs font-semibold text-slate-300">Тема одного ролика</label>
                    <span className="text-[10px] text-slate-500">{form.topic.length}/200</span>
                  </div>
                  <textarea
                    required
                    minLength={3}
                    maxLength={200}
                    rows={3}
                    className="field text-sm leading-relaxed resize-none"
                    value={form.topic}
                    onChange={(e) => setField("topic")(e.target.value)}
                    placeholder="Например: Секрет вечной молодости голых землекопов..."
                  />

                  <div className="mt-2">
                    <div className="text-[10px] font-medium text-slate-400 mb-1">Быстрые идеи:</div>
                    <div className="flex flex-wrap gap-1">
                      {QUICK_TOPICS.map((t, idx) => (
                        <button
                          key={idx}
                          type="button"
                          onClick={() => setField("topic")(t)}
                          className="text-[10px] bg-studio-850 hover:bg-studio-800 text-slate-300 hover:text-indigo-300 px-2 py-0.5 rounded border border-slate-700/60 transition truncate max-w-full"
                        >
                          {t}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Presets */}
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5">Стиль ролика</label>
                  <div className="grid grid-cols-3 gap-1.5">
                    {PRESET_CARDS.map((p) => {
                      const active = form.preset === p.id;
                      return (
                        <button
                          key={p.id}
                          type="button"
                          onClick={() => {
                            setField("preset")(p.id);
                            if (p.id === "horror_rules") {
                              setField("sub_style")("horror");
                              setField("cta")("Вторая часть и секретные протоколы выживания по ссылке в шапке профиля 👆");
                            }
                          }}
                          className={`p-2 rounded-xl text-left border transition-all ${
                            active
                              ? "bg-indigo-600/20 border-indigo-500 text-white shadow-glow"
                              : "bg-studio-850/60 border-slate-800 text-slate-400 hover:border-slate-700"
                          }`}
                        >
                          <div className="text-sm mb-0.5">{p.icon}</div>
                          <div className="text-[11px] font-bold leading-tight truncate">{p.title}</div>
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* Subtitle Styles */}
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5">Субтитры</label>
                  <div className="grid grid-cols-2 gap-1.5">
                    {[
                      { id: "ref", label: "🎯 Как в референсе (по словам)" },
                      { id: "mrbeast", label: "🟡 MrBeast Жёлтый" },
                      { id: "neon", label: "💎 Неоновый Циан" },
                      { id: "clean", label: "⚪ Чистый Белый" },
                      { id: "gold", label: "👑 Luxury Золото" },
                    ].map((s) => (
                      <button
                        key={s.id}
                        type="button"
                        onClick={() => setField("sub_style")(s.id)}
                        className={`p-2 rounded-xl text-xs font-bold border transition text-left ${
                          form.sub_style === s.id
                            ? "bg-indigo-600/30 border-indigo-500 text-white shadow-glow"
                            : "bg-studio-850/60 border-slate-800 text-slate-400"
                        }`}
                      >
                        {s.label}
                      </button>
                    ))}
                  </div>
                </div>

                {/* AI Script Provider */}
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    AI-генератор сценария
                  </label>
                  <div className="grid grid-cols-2 gap-1.5">
                    {[
                      { id: "qwen", label: "🦙 Qwen Local" },
                      { id: "gemini", label: "✨ Gemini (Беспл.)" },
                    ].map((m) => (
                      <button
                        key={m.id}
                        type="button"
                        onClick={() => setField("script")(m.id)}
                        className={`p-1.5 rounded-lg text-xs font-semibold border transition text-center ${
                          form.script === m.id
                            ? "bg-indigo-600/30 border-indigo-500 text-white shadow-glow"
                            : "bg-studio-850/60 border-slate-800 text-slate-400 hover:text-slate-200"
                        }`}
                      >
                        {m.label}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Visuals Provider */}
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Генератор видеоряда
                  </label>
                  <div className="grid grid-cols-2 gap-1.5">
                    {[
                      { id: "motion_gfx", label: "🎞️ Motion graphics (стиль референса, без GPU)" },
                      { id: "ai_video", label: "🎬 AI Видеодиффузия (SVD-XT на GPU)" },
                      { id: "ai_scenes", label: "⚡ Быстрый AI-кадр (Ken Burns 60 FPS)" },
                      { id: "kling", label: "🌐 Облачные видеосети (Kling / Runway)" },
                    ].map((v) => (
                      <button
                        key={v.id}
                        type="button"
                        onClick={() => setField("visuals")(v.id)}
                        className={`p-1.5 rounded-lg text-[11px] font-semibold border transition text-center ${
                          form.visuals === v.id
                            ? "bg-indigo-600/30 border-indigo-500 text-white shadow-glow"
                            : "bg-studio-850/60 border-slate-800 text-slate-400 hover:text-slate-200"
                        }`}
                      >
                        {v.label}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Scene designer */}
                {form.visuals === "motion_gfx" && (
                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1">
                      Художник сцен (рисует новую сцену под фразу)
                    </label>
                    <div className="grid grid-cols-2 gap-1.5">
                      {[
                        { id: "auto", label: "🎨 Авто: нужные биты, LLM + словарь" },
                        { id: "all", label: "🖌️ Все биты рисуем заново" },
                        { id: "heuristic", label: "⚡ Быстро: по словарю, без LLM" },
                        { id: "off", label: "📦 Только готовые сцены" },
                      ].map((v) => (
                        <button
                          key={v.id}
                          type="button"
                          onClick={() => setField("scene_gen")(v.id)}
                          className={`p-1.5 rounded-lg text-[11px] font-semibold border transition text-center ${
                            form.scene_gen === v.id
                              ? "bg-indigo-600/30 border-indigo-500 text-white shadow-glow"
                              : "bg-studio-850/60 border-slate-800 text-slate-400 hover:text-slate-200"
                          }`}
                        >
                          {v.label}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* Language & Voice */}
                <div className="grid grid-cols-2 gap-2.5">
                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1">Язык</label>
                    <select
                      className="field text-xs"
                      value={form.lang}
                      onChange={(e) => setForm((prev) => ({ ...prev, lang: e.target.value, voice: "" }))}
                    >
                      <option value="ru">🇷🇺 Русский</option>
                      <option value="en">🇺🇸 English</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1">Голос</label>
                    <select
                      className="field text-xs"
                      value={form.voice}
                      onChange={(e) => setField("voice")(e.target.value)}
                    >
                      <option value="">По умолчанию</option>
                      {voices.map((v) => (
                        <option key={v.id} value={v.id}>
                          {v.label}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                {/* Mock Mode Switch */}
                <label className="flex items-start gap-2.5 p-2.5 rounded-xl bg-studio-850/60 border border-slate-800 cursor-pointer">
                  <input
                    type="checkbox"
                    className="mt-0.5 h-4 w-4 rounded border-slate-700 bg-studio-900 text-indigo-600"
                    checked={form.mock}
                    onChange={(e) => setField("mock")(e.target.checked)}
                  />
                  <div className="text-xs">
                    <span className="font-bold text-slate-200">Mock Mode</span>
                    <p className="text-[10px] text-slate-400">Быстрый тест без траты API токенов</p>
                  </div>
                </label>

                {err && (
                  <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs">
                    {err}
                  </div>
                )}

                <button
                  type="submit"
                  disabled={isRunning || !backendOnline}
                  className={`w-full py-3.5 px-4 rounded-xl font-bold text-sm text-white flex items-center justify-center gap-2 transition-all shadow-glow ${
                    isRunning
                      ? "bg-slate-700 cursor-not-allowed opacity-80"
                      : "bg-indigo-600 hover:bg-indigo-500 active:scale-[0.99]"
                  }`}
                >
                  {isRunning ? (
                    <>
                      <span className="animate-spin text-base">⚙️</span>
                      <span>Генерация... ({elapsedSec}s)</span>
                    </>
                  ) : (
                    <>
                      <Icons.Sparkles />
                      <span>Создать одиночное видео</span>
                    </>
                  )}
                </button>
              </form>
            )}
          </div>
        </section>

        {/* ================= COLUMN 2: Pipeline Status & Library (5 cols) ================= */}
        <section className="lg:col-span-5 space-y-4">
          {/* Active Job & Batch Progress Card */}
          <div className="glass-panel rounded-2xl p-5 shadow-2xl border border-slate-800 space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <Icons.Terminal /> Статус рендера
              </h2>
              {batchProgress?.status === "running" ? (
                <span className="text-[11px] font-bold px-2.5 py-0.5 rounded-full bg-cyan-500/20 text-cyan-300 animate-pulse border border-cyan-500/30">
                  Пакет: {batchProgress.completed}/{batchProgress.total} готово ({elapsedSec}s)
                </span>
              ) : job ? (
                <span
                  className={`text-[11px] font-bold px-2.5 py-0.5 rounded-full ${
                    job.status === "running"
                      ? "bg-indigo-500/20 text-indigo-300 animate-pulse border border-indigo-500/30"
                      : job.status === "done"
                      ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
                      : "bg-rose-500/20 text-rose-300 border border-rose-500/30"
                  }`}
                >
                  {job.status === "running" ? `В работе (${elapsedSec}s)` : job.status === "done" ? "Завершено" : "Ошибка"}
                </span>
              ) : null}
            </div>

            {/* Batch Progress Bar if active */}
            {batchProgress && (
              <div className="rounded-xl bg-studio-900/80 p-3 border border-slate-800 space-y-2">
                <div className="flex items-center justify-between text-xs font-semibold">
                  <span className="text-slate-300 flex items-center gap-1.5">
                    <Icons.Layers /> Очередь пакета:
                  </span>
                  <span className="text-cyan-400 font-mono">
                    {batchProgress.completed} из {batchProgress.total} видео
                  </span>
                </div>
                <div className="w-full bg-studio-950 rounded-full h-2.5 overflow-hidden border border-slate-800">
                  <div
                    className="bg-gradient-to-r from-indigo-500 to-cyan-400 h-full transition-all duration-500 rounded-full"
                    style={{
                      width: `${Math.round((batchProgress.completed / Math.max(1, batchProgress.total)) * 100)}%`,
                    }}
                  />
                </div>
                {batchProgress.current_topic && (
                  <div className="text-[10px] text-slate-400 truncate">
                    Текущая тема: <span className="text-slate-200">{batchProgress.current_topic}</span>
                  </div>
                )}
              </div>
            )}

            {/* Pipeline Stage Tracker */}
            <div className="grid grid-cols-5 gap-1.5 pt-1">
              {(opts?.stages || ["Сценарий", "Озвучка", "Визуал", "Рендер", "Готово"]).map((stageName, idx) => {
                const isCurrent = job?.status === "running" && job?.stage === idx;
                const isPassed = job?.status === "done" || (job && job.stage > idx);
                const isError = job?.status === "error" && job?.stage === idx;

                return (
                  <div
                    key={stageName}
                    className={`rounded-xl p-2 text-center transition-all border ${
                      isCurrent
                        ? "bg-indigo-600/30 border-indigo-500 text-white shadow-glow scale-[1.02]"
                        : isPassed
                        ? "bg-emerald-950/40 border-emerald-500/40 text-emerald-300"
                        : isError
                        ? "bg-rose-950/40 border-rose-500 text-rose-300"
                        : "bg-studio-850/40 border-slate-800/80 text-slate-500"
                    }`}
                  >
                    <div className="text-sm mb-1">{STAGE_ICONS[idx]}</div>
                    <div className="text-[10px] font-bold truncate">{stageName}</div>
                  </div>
                );
              })}
            </div>

            {/* Terminal Live Logs */}
            <div className="relative">
              <div className="flex items-center justify-between text-[11px] text-slate-400 mb-1 px-1">
                <span>Лог пайплайна FFmpeg & AI</span>
                {job?.logs?.length > 0 && (
                  <button
                    onClick={() => copyText(job.logs.join("\n"), "logs")}
                    className="hover:text-indigo-300 flex items-center gap-1 transition"
                  >
                    {copiedKey === "logs" ? <Icons.Check /> : <Icons.Copy />}
                    <span>{copiedKey === "logs" ? "Скопировано" : "Копировать"}</span>
                  </button>
                )}
              </div>
              <pre
                ref={logRef}
                className="h-44 overflow-y-auto rounded-xl bg-black/70 p-3 font-mono text-[11px] leading-relaxed text-slate-300 border border-slate-800/80 shadow-inner"
              >
                {job?.logs?.length ? (
                  job.logs.map((line, i) => {
                    let color = "text-slate-300";
                    if (line.includes("ОШИБКА")) color = "text-rose-400 font-bold";
                    else if (line.includes("Готово!")) color = "text-emerald-400 font-bold";
                    else if (line.includes("Хук:")) color = "text-indigo-300";
                    else if (line.includes("Рендерим")) color = "text-cyan-300";
                    return (
                      <div key={i} className={color}>
                        {line}
                      </div>
                    );
                  })
                ) : (
                  <span className="text-slate-600">Нажмите кнопку генерации для старта рендера.</span>
                )}
              </pre>
            </div>

            {/* Active Video: Ready-to-Publish Post for TikTok / Reels / TG */}
            {current && (
              <div className="rounded-xl bg-studio-850/80 p-3.5 border border-slate-800 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-white flex items-center gap-1.5">
                    <span className="text-cyan-400">📋</span> Готовый пост для TikTok / Reels / TG
                  </span>
                  {current.post_text && (
                    <button
                      onClick={() => copyText(current.post_text, "post_text")}
                      className="text-xs bg-indigo-600 hover:bg-indigo-500 text-white px-2.5 py-1 rounded-lg font-bold flex items-center gap-1.5 transition shadow-glow"
                    >
                      {copiedKey === "post_text" ? <Icons.Check /> : <Icons.Copy />}
                      <span>{copiedKey === "post_text" ? "Скопировано!" : "Скопировать пост"}</span>
                    </button>
                  )}
                </div>

                <div className="bg-studio-900/80 p-3 rounded-lg border border-slate-800 text-xs space-y-2">
                  <div className="font-semibold text-slate-200">
                    {current.post_caption || current.title}
                  </div>
                  {current.cta && (
                    <div className="text-indigo-300 font-medium">
                      👉 {current.cta}
                    </div>
                  )}
                  {current.hashtags && current.hashtags.length > 0 && (
                    <div className="flex flex-wrap gap-1 pt-1 border-t border-slate-800/80">
                      {current.hashtags.map((tag, idx) => (
                        <span key={idx} className="text-[10px] text-cyan-400 bg-cyan-950/40 px-1.5 py-0.5 rounded border border-cyan-800/40">
                          #{tag.replace(/^#/, "")}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                {/* Director & Visual Engine Telemetry (Ф1, Ф9) */}
                {(current.director || current.scene_reasons) && (
                  <div className="bg-studio-950/70 p-2.5 rounded-lg border border-slate-800 text-[11px] space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-slate-400 flex items-center gap-1">
                        🎬 <strong>Режиссёр:</strong>
                      </span>
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          current.director?.source === "fallback"
                            ? "bg-amber-950/60 text-amber-300 border border-amber-600/40"
                            : "bg-emerald-950/60 text-emerald-300 border border-emerald-600/40"
                        }`}
                      >
                        {current.director?.source || "auto"}{" "}
                        {current.director?.model ? `(${current.director.model})` : ""}
                      </span>
                    </div>

                    {current.scene_reasons && Object.keys(current.scene_reasons).length > 0 && (
                      <div className="flex items-center gap-1.5 flex-wrap pt-1 border-t border-slate-800/80">
                        <span className="text-slate-400 text-[10px]">Причины выбора сцен:</span>
                        {Object.entries(current.scene_reasons).map(([reason, cnt]) => (
                          <span
                            key={reason}
                            className="px-1.5 py-0.5 rounded text-[10px] bg-indigo-950/60 text-indigo-300 border border-indigo-800/40 font-mono"
                          >
                            {reason}: {cnt}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Video Library Card */}
          <div className="glass-panel rounded-2xl p-5 shadow-2xl border border-slate-800 space-y-3">
            <div className="flex items-center justify-between">
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <Icons.Film /> Готовые ролики ({videos.length})
              </h2>
              <button onClick={loadVideos} className="text-xs text-slate-400 hover:text-white flex items-center gap-1">
                <Icons.Refresh />
              </button>
            </div>

            {videos.length === 0 ? (
              <div className="text-center py-8 text-xs text-slate-500">
                Библиотека пуста. Запустите пакетную генерацию слева!
              </div>
            ) : (
              <div className="max-h-64 overflow-y-auto space-y-2 pr-1">
                {videos.map((v) => {
                  const isSelected = current?.id === v.id;
                  return (
                    <div
                      key={v.id}
                      onClick={() => setCurrent(v)}
                      className={`flex items-center justify-between p-3 rounded-xl border cursor-pointer transition-all ${
                        isSelected
                          ? "bg-indigo-600/20 border-indigo-500/80 shadow-glow"
                          : "bg-studio-850/50 border-slate-800 hover:border-slate-700 hover:bg-studio-850"
                      }`}
                    >
                      <div className="flex items-center gap-3 min-w-0 pr-2">
                        <div
                          className={`h-9 w-9 rounded-lg flex items-center justify-center shrink-0 ${
                            isSelected ? "bg-indigo-600 text-white" : "bg-studio-800 text-slate-400"
                          }`}
                        >
                          <Icons.Play />
                        </div>
                        <div className="min-w-0">
                          <h4 className="text-xs font-bold text-white truncate">{v.title}</h4>
                          <div className="flex items-center gap-2 text-[10px] text-slate-400 mt-0.5">
                            <span>⏱️ {v.duration}s</span>
                            <span>•</span>
                            <span>{v.created}</span>
                            {v.sfx_count ? (
                              <span className="text-amber-400 font-mono">🔊 {v.sfx_count} SFX</span>
                            ) : null}
                            {v.progress_bar ? (
                              <span className="text-emerald-400 font-mono">⚡ Bar</span>
                            ) : null}
                            {v.sub_style && (
                              <span className="text-cyan-400 font-mono">[{v.sub_style}]</span>
                            )}
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center gap-1.5 shrink-0" onClick={(e) => e.stopPropagation()}>
                        <a
                          href={v.url}
                          download={`${v.id}.mp4`}
                          className="p-1.5 rounded-lg bg-studio-800 hover:bg-studio-700 text-slate-300 hover:text-white transition"
                          title="Скачать MP4"
                        >
                          <Icons.Download />
                        </a>
                        <button
                          onClick={(e) => deleteVideo(v.id, e)}
                          className="p-1.5 rounded-lg bg-studio-800 hover:bg-rose-900/60 text-slate-400 hover:text-rose-300 transition"
                          title="Удалить"
                        >
                          <Icons.Trash />
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </section>

        {/* ================= COLUMN 3: Vertical 9:16 Smartphone Player (3 cols) ================= */}
        <aside className="lg:col-span-3 flex flex-col items-center">
          <div className="w-full max-w-[280px]">
            {/* Realistic iPhone / Vertical Display Frame */}
            <div className="relative rounded-[36px] p-2 bg-gradient-to-b from-slate-700 via-slate-800 to-slate-900 shadow-phone border border-slate-700/60">
              {/* Dynamic Island Speaker Notch */}
              <div className="absolute top-4 left-1/2 -translate-x-1/2 w-20 h-4 bg-black rounded-full z-20 flex items-center justify-end px-2">
                <div className="h-2 w-2 rounded-full bg-slate-900 border border-slate-700/50" />
              </div>

              {/* Screen Container 9:16 */}
              <div className="relative aspect-[9/16] w-full rounded-[28px] overflow-hidden bg-black flex items-center justify-center">
                {current ? (
                  <video
                    ref={videoPlayerRef}
                    key={current.url}
                    src={current.url}
                    controls
                    autoPlay
                    loop
                    className="h-full w-full object-cover"
                  />
                ) : (
                  <div className="p-6 text-center text-xs text-slate-500 space-y-2">
                    <div className="text-3xl opacity-40">📱</div>
                    <p className="font-medium text-slate-400">Предпросмотр 9:16</p>
                    <p className="text-[10px] text-slate-600">Здесь появится видео 1080×1920 с субтитрами</p>
                  </div>
                )}

                {/* Quality Badge Overlay */}
                {current && (
                  <div className="absolute top-8 left-3 z-10 pointer-events-none">
                    <span className="bg-black/70 backdrop-blur-md text-[9px] text-cyan-300 font-mono px-2 py-0.5 rounded-full border border-cyan-500/30">
                      60 FPS • {current.sfx_count ? `${current.sfx_count} SFX • ` : ""}Audio Ducking • Retention Bar
                    </span>
                  </div>
                )}
              </div>
            </div>

            {/* Quick Actions & Meta under phone */}
            {current && (
              <div className="mt-4 space-y-2 text-center">
                <h3 className="text-xs font-bold text-white truncate px-2">{current.title}</h3>
                <div className="flex items-center justify-center gap-2">
                  <a
                    href={current.url}
                    download={`${current.id}.mp4`}
                    className="flex-1 py-2 px-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs flex items-center justify-center gap-1.5 transition shadow-glow"
                  >
                    <Icons.Download />
                    <span>Скачать MP4</span>
                  </a>
                  <button
                    onClick={() => copyText(window.location.origin + current.url, "url")}
                    className="py-2 px-3 rounded-xl bg-studio-850 hover:bg-studio-800 text-slate-300 text-xs font-medium border border-slate-700 transition"
                    title="Скопировать ссылку на видео"
                  >
                    {copiedKey === "url" ? <Icons.Check /> : <Icons.Copy />}
                  </button>
                </div>
              </div>
            )}
          </div>
        </aside>
      </main>

      {/* --- Footer --- */}
      <footer className="border-t border-slate-800/80 bg-studio-900/40 py-3 text-center text-xs text-slate-500">
        Vertical Video Studio • Пакетная генерация 60 FPS • TikTok, Instagram Reels & Telegram
      </footer>
    </div>
  );
}
