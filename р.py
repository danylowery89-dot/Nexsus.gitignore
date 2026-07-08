from http.server import HTTPServer, BaseHTTPRequestHandler
import os
import base64

# Умное определение папки, где лежит этот скрипт р.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Пытаемся прочитать картинку и превратить её в текст (Base64)
image_base64 = ""
for filename in ['my_photo.jpg', 'my_photo.jpg.jpg', 'my_photo.png']:
    full_path = os.path.join(BASE_DIR, filename)
    if os.path.exists(full_path):
        with open(full_path, 'rb') as img_file:
            image_base64 = base64.b64encode(img_file.read()).decode('utf-8')
        break

# Если картинка нашлась, создаем для неё аккуратный контейнер с кнопками управления
if image_base64:
    img_tag = f"""
    <div class="relative group max-w-md my-2 rounded-2xl overflow-hidden border border-white/10 bg-black/20 shadow-2xl">
        <img id="nexus-target-img" src="data:image/jpeg;base64,{image_base64}" class="w-full max-h-[450px] object-cover transition duration-300 group-hover:scale-[1.01]">

        <div class="absolute bottom-0 inset-x-0 bg-gradient-to-t from-black/90 via-black/50 to-transparent p-4 flex justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300 z-10">
            <button onclick="zoomMedia('image')" class="px-3 py-1.5 bg-white/10 hover:bg-white/20 text-white rounded-lg text-[10px] font-bold uppercase tracking-wider backdrop-blur-sm transition">
                🔍 Экран
            </button>
            <button onclick="downloadImage()" class="px-3 py-1.5 bg-white/10 hover:bg-white/20 text-white rounded-lg text-[10px] font-bold uppercase tracking-wider backdrop-blur-sm transition">
                💾 Скачать
            </button>
            <button onclick="shareImage()" class="px-3 py-1.5 bg-zinc-900/80 hover:bg-white text-zinc-400 hover:text-black rounded-lg text-[10px] font-bold uppercase tracking-wider backdrop-blur-sm transition">
                🔗 Ссылка
            </button>
        </div>
    </div>
    """
else:
    expected_path = os.path.join(BASE_DIR, "my_photo.jpg")
    img_tag = f'<p style="color:#ff3333; font-weight:bold;">[Система: Положите картинку сюда -> {expected_path}]</p>'

# --- ОБРАБОТКА ТВОЕГО ЗАГОТОВЛЕННОГО ВИДЕО ---
video_filename = "my_dance.mp4"
video_full_path = os.path.join(BASE_DIR, video_filename)

if os.path.exists(video_full_path):
    video_source_url = "/get_video"
    video_error_msg = ""
else:
    video_source_url = ""
    video_error_msg = f'<p style="color:#ff3333; padding: 15px; font-weight:bold;">[Ошибка: Файл {video_filename} не найден в {BASE_DIR}!]</p>'

# --- ОБРАБОТКА ТВОЕГО ЗАГОТОВЛЕННОГО АУДИО (БИТА) ---
audio_filename = "my_beat.mp3"
audio_full_path = os.path.join(BASE_DIR, audio_filename)

if os.path.exists(audio_full_path):
    audio_source_url = "/get_beat"
    audio_error_msg = ""
else:
    audio_source_url = ""
    audio_error_msg = f'<p style="color:#ff3333; padding: 15px; font-weight:bold;">[Ошибка: Файл {audio_filename} не найден в {BASE_DIR}!]</p>'

# Сам код страницы (чистый текст)
html_code = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NEXUS AI | Core v.5.2 Quantum</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght=200;400;600;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --acid: #d4ff00;
            --acid-dim: rgba(212, 255, 0, 0.1);
            --bg: #050605;
            --panel: rgba(18, 20, 18, 0.98);
        }
        body { background: var(--bg); color: #e4e4e4; font-family: 'Plus Jakarta Sans', sans-serif; overflow-x: hidden; scroll-behavior: smooth; }
        .glass { background: var(--panel); backdrop-filter: blur(25px); border: 1px solid rgba(212, 255, 0, 0.08); }
        .acid-text { color: var(--acid); }
        .acid-bg { background-color: var(--acid); }

        .btn-acid { background: var(--acid); color: #000; font-weight: 800; transition: 0.3s; text-transform: uppercase; letter-spacing: 1px; }
        .btn-acid:hover { box-shadow: 0 0 30px rgba(212, 255, 0, 0.3); transform: scale(1.02); }

        .auth-input { 
            background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1);
            border-radius: 12px; padding: 12px 16px; font-size: 14px; outline: none; transition: 0.3s; color: white;
        }
        .auth-input:focus { border-color: var(--acid); background: rgba(212, 255, 0, 0.02); }

        .fade-in { animation: fadeIn 0.6s ease-out forwards; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(15px); } to { opacity: 1; transform: translateY(0); } }

        .gen-loader { width: 100%; height: 3px; background: rgba(255,255,255,0.05); border-radius: 10px; overflow: hidden; margin-top: 10px; }
        .gen-progress { width: 0%; height: 100%; background: var(--acid); animation: progress 3s ease-in-out forwards; }
        @keyframes progress { to { width: 100%; } }

        .typing::after { content: '_'; animation: blink 0.8s infinite; }
        @keyframes blink { 50% { opacity: 0; } }

        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-thumb { background: var(--acid); border-radius: 10px; }

        .history-card { transition: 0.3s; border-left: 2px solid transparent; }
        .history-card.active { border-color: var(--acid); background: rgba(212, 255, 0, 0.08); }

        /* Стилизация аудио плеера под тему Acid */
        audio::-webkit-media-controls-panel { background-color: rgba(18, 20, 18, 0.95); border: 1px solid rgba(212, 255, 0, 0.2); }
        audio::-webkit-media-controls-current-time-display,
        audio::-webkit-media-controls-time-remaining-display { color: #d4ff00; }

        /* Плавная анимация карточек тарифов при наведении */
        .tariff-card {
            transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.4s ease, border-color 0.4s ease;
        }
        .tariff-card:hover {
            transform: translateY(-8px) scale(1.02);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.6), 0 0 30px rgba(212, 255, 0, 0.05);
            border-color: rgba(212, 255, 0, 0.2);
        }
        .tariff-card.premium-highlight:hover {
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.7), 0 0 35px rgba(212, 255, 0, 0.2);
            border-color: var(--acid);
        }
    </style>
</head>
<body>

    <nav class="fixed top-0 w-full z-50 p-4">
        <div class="max-w-7xl mx-auto flex justify-between items-center glass rounded-2xl px-8 py-4">
            <div class="flex items-center gap-3">
                <div class="w-3 h-3 acid-bg rounded-full animate-pulse"></div>
                <span class="font-black italic text-xl tracking-tighter uppercase">NEXUS <span class="acid-text">AI</span></span>
            </div>
            <div class="hidden lg:flex gap-10 text-[10px] font-bold uppercase tracking-[0.2em]">
                <a href="#about" class="hover:acid-text transition">О Платформе</a>
                <a href="#features" class="hover:acid-text transition">Технологии</a>
                <a href="#workflow" class="hover:acid-text transition">Как это работает</a>
                <a href="#tariffs" class="hover:acid-text transition">Тарифы</a>
                <a href="#faq" class="hover:acid-text transition">FAQ</a>
            </div>
            <div class="flex items-center gap-4">
                <div class="flex bg-white/5 rounded-full p-1 border border-white/10 text-[10px]">
                    <button onclick="setLang('ru')" id="lang-ru" class="px-3 py-1 rounded-full bg-white/10">RU</button>
                    <button onclick="setLang('en')" id="lang-en" class="px-3 py-1 rounded-full text-zinc-500">EN</button>
                </div>
                <button onclick="showAuth('login')" class="btn-acid px-6 py-2 rounded-full text-[10px]">Вход</button>
            </div>
        </div>
    </nav>

    <div id="landing-page" class="relative h-screen overflow-y-auto scroll-smooth">

        <section class="pt-64 pb-20 px-6 text-center">
            <h1 class="text-7xl md:text-9xl font-black italic uppercase tracking-tighter mb-8 leading-none">
                Quantum <span class="acid-text">Mind</span> 2026
            </h1>
            <p class="max-w-3xl mx-auto text-zinc-500 mb-12 text-lg leading-relaxed">
                NEXUS AI — мультимодальная среда нового поколения. Текст, фото, video и музыка в одном квантовом контуре.
            </p>
            <div class="flex justify-center gap-6 mb-20">
                <button onclick="showAuth('signup')" class="btn-acid px-12 py-5 rounded-2xl text-xs">Начать генерацию</button>
                <div class="flex flex-col items-start justify-center px-6 border-l border-white/10">
                    <span class="text-xl font-black italic">2.4M+</span>
                    <span class="text-[9px] uppercase text-zinc-600 font-bold">Активных пользователей</span>
                </div>
            </div>
        </section>

        <section class="max-w-7xl mx-auto px-6 py-12 grid grid-cols-2 md:grid-cols-4 gap-6 text-center border-y border-white/5 bg-white/[0.01]">
            <div class="p-6">
                <div class="text-3xl md:text-4xl font-black italic acid-text mb-1">99.98%</div>
                <div class="text-[9px] text-zinc-500 uppercase font-bold tracking-widest">Аптайм квантовых ядер</div>
            </div>
            <div class="p-6">
                <div class="text-3xl md:text-4xl font-black italic text-white mb-1">14.2 Пб</div>
                <div class="text-[9px] text-zinc-500 uppercase font-bold tracking-widest">Сгенерированных медиаданных</div>
            </div>
            <div class="p-6">
                <div class="text-3xl md:text-4xl font-black italic text-white mb-1">&lt; 1.4 сек</div>
                <div class="text-[9px] text-zinc-500 uppercase font-bold tracking-widest">Средняя скорость инференса</div>
            </div>
            <div class="p-6">
                <div class="text-3xl md:text-4xl font-black italic text-white mb-1">50+</div>
                <div class="text-[9px] text-zinc-500 uppercase font-bold tracking-widest">Интегрированных ИИ-моделей</div>
            </div>
        </section>

        <section id="about" class="max-w-7xl mx-auto px-6 py-24 grid md:grid-cols-2 gap-20 items-center">
            <div class="glass p-12 rounded-[3rem] border-white/5">
                <span class="text-[9px] font-black uppercase tracking-widest acid-text">О Платформе</span>
                <h2 class="text-4xl font-black italic uppercase mt-2 mb-8">Экосистема Nexus Systems</h2>
                <p class="text-zinc-400 mb-6 leading-relaxed">Мы основаны в 2024 году командой исследователей систем глубокого машинного обучения. Наша цель — убрать барьеры между разрозненными ИИ-генераторами и объединить текст, графику, звук и динамическое видео в единый бесшовный Workspace.</p>
                <p class="text-zinc-500 text-sm leading-relaxed">В 2026 году Nexus AI оперирует распределенными вычислительными кластерами повышенной энергоэффективности, предоставляя доступ к нейросетям без цензурных задержек и сложных настроек окружения.</p>
                <div class="grid grid-cols-2 gap-4 mt-10">
                    <div class="p-4 bg-white/5 rounded-2xl border border-white/5">
                        <div class="text-xs font-bold acid-text mb-1">Шифрование</div>
                        <div class="text-[10px] text-zinc-500 uppercase">AES-Quantum 2048</div>
                    </div>
                    <div class="p-4 bg-white/5 rounded-2xl border border-white/5">
                        <div class="text-xs font-bold acid-text mb-1">Доверие</div>
                        <div class="text-[10px] text-zinc-500 uppercase">ISO 9001:2026</div>
                    </div>
                </div>
            </div>
            <div class="space-y-8">
                <span class="text-[9px] font-black uppercase tracking-widest text-zinc-600">Архитектурный стек</span>
                <h3 class="text-3xl font-black italic uppercase">Универсальный ИИ-Контур</h3>
                <p class="text-zinc-400">Больше не нужно оплачивать 5 разных подписок. Наша нейросетевая матрица динамически перенаправляет ваши запросы на специализированные узлы:</p>

                <div class="space-y-4">
                    <div class="p-4 glass rounded-2xl flex items-center gap-4">
                        <div class="w-8 h-8 rounded-full bg-white/5 flex items-center justify-center font-bold text-xs acid-text">01</div>
                        <div>
                            <div class="text-xs font-black uppercase">Языковые модели сверхвысокого объема</div>
                            <div class="text-[10px] text-zinc-500">Прямой коннект к пулам DeepSeek V3, Claude 4.8 и GPT-5.5</div>
                        </div>
                    </div>
                    <div class="p-4 glass rounded-2xl flex items-center gap-4">
                        <div class="w-8 h-8 rounded-full bg-white/5 flex items-center justify-center font-bold text-xs acid-text">02</div>
                        <div>
                            <div class="text-xs font-black uppercase">Диффузионный рендеринг медиа</div>
                            <div class="text-[10px] text-zinc-500">Генерация реалистичного видео через Kling 3.0 и аудио через Suno HQ</div>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <section id="features" class="max-w-7xl mx-auto px-6 py-24 border-t border-white/5">
            <div class="text-center mb-16">
                <span class="text-[9px] font-black uppercase tracking-widest acid-text">Почему мы</span>
                <h2 class="text-4xl md:text-5xl font-black italic uppercase mt-2">Превосходство в деталях</h2>
            </div>
            <div class="grid md:grid-cols-3 gap-8">
                <div class="p-8 glass rounded-[2.5rem] border-white/5">
                    <div class="text-2xl mb-4">⚡</div>
                    <h4 class="text-md font-black uppercase mb-2">Мгновенный Инференс</h4>
                    <p class="text-xs text-zinc-500 leading-relaxed">Наша кастомная балансировка нагрузок распределяет запросы за миллисекунды. Забудьте про очереди.</p>
                </div>
                <div class="p-8 glass rounded-[2.5rem] border-white/5">
                    <div class="text-2xl mb-4">🔏</div>
                    <h4 class="text-md font-black uppercase mb-2">Абсолютный инкогнито-режим</h4>
                    <p class="text-xs text-zinc-500 leading-relaxed">Мы не логируем промпты и не используем ваши генерации для обучения публичных моделей. Все строго конфиденциально.</p>
                </div>
                <div class="p-8 glass rounded-[2.5rem] border-white/5">
                    <div class="text-2xl mb-4">🔗</div>
                    <h4 class="text-md font-black uppercase mb-2">Разработчикам (API)</h4>
                    <p class="text-xs text-zinc-500 leading-relaxed">Интегрируйте генерацию картинок, текста и музыки в свои приложения через единый REST API ключ.</p>
                </div>
            </div>
        </section>

        <section id="workflow" class="max-w-7xl mx-auto px-6 py-24 border-t border-white/5">
            <div class="text-center mb-16">
                <span class="text-[9px] font-black uppercase tracking-widest acid-text">Процесс создания</span>
                <h2 class="text-4xl md:text-5xl font-black italic uppercase mt-2">Три шага к результату</h2>
            </div>
            <div class="grid md:grid-cols-3 gap-12 relative">
                <div class="flex flex-col items-center text-center">
                    <div class="w-16 h-16 rounded-full glass border border-acid/30 flex items-center justify-center font-black text-lg text-white mb-6">1</div>
                    <h4 class="text-xs font-black uppercase mb-2 tracking-wider">Выбор ИИ-Ядра</h4>
                    <p class="text-[11px] text-zinc-500 max-w-xs leading-relaxed">Выберите нужную модель в выпадающем меню: от текстового ассистента до видеогенератора Kling.</p>
                </div>
                <div class="flex flex-col items-center text-center">
                    <div class="w-16 h-16 rounded-full glass border border-acid/30 flex items-center justify-center font-black text-lg text-white mb-6">2</div>
                    <h4 class="text-xs font-black uppercase mb-2 tracking-wider">Ввод промпта</h4>
                    <p class="text-[11px] text-zinc-500 max-w-xs leading-relaxed">Напишите запрос на любом удобном языке. Наш внутренний переводчик оптимизирует ТЗ под выбранное ИИ-ядро.</p>
                </div>
                <div class="flex flex-col items-center text-center">
                    <div class="w-16 h-16 rounded-full glass border border-acid/50 flex items-center justify-center font-black text-lg acid-bg text-black mb-6 animate-pulse">3</div>
                    <h4 class="text-xs font-black uppercase mb-2 tracking-wider acid-text">Готовый медиа-пак</h4>
                    <p class="text-[11px] text-zinc-500 max-w-xs leading-relaxed">Скачивайте, масштабируйте или делитесь результатом по прямой ссылке прямо из окна стрима.</p>
                </div>
            </div>
        </section>

        <section id="tariffs" class="max-w-7xl mx-auto px-6 py-24 border-t border-white/5">
            <h2 class="text-5xl font-black italic uppercase text-center mb-20 acid-text">Тарифные планы</h2>
            <div class="grid md:grid-cols-3 gap-8">

                <div class="tariff-card glass p-10 rounded-[3rem] border border-white/5 flex flex-col justify-between relative overflow-hidden">
                    <div>
                        <div class="text-4xl font-black italic mb-2 uppercase text-zinc-400">Base</div>
                        <div class="text-xs font-bold text-zinc-500 uppercase tracking-wider mb-6">Ознакомительный режим</div>
                        <ul class="text-xs space-y-4 mb-12 text-zinc-400 font-medium">
                            <li class="flex items-center gap-2">✅ Текст: Базовый GPT 5.5 / DeepSeek</li>
                            <li class="flex items-center gap-2">❌ Фото: Лимитировано (Низкое разрешение)</li>
                            <li class="flex items-center gap-2 text-red-500/80">❌ Видео: Заблокировано в вашей версии</li>
                            <li class="flex items-center gap-2 text-red-500/80">❌ Аудио: 1 генерация в сутки</li>
                            <li class="flex items-center gap-2">❌ Очередь: Длинное время ожидания</li>
                        </ul>
                    </div>
                    <div>
                        <div class="text-4xl font-black italic mb-8">$0</div>
                        <button onclick="showAuth('signup')" class="w-full py-5 border border-zinc-800 hover:border-zinc-700 rounded-2xl text-[10px] font-black uppercase tracking-wider transition">Выбрать</button>
                    </div>
                </div>

                <div class="tariff-card premium-highlight glass p-10 rounded-[3rem] border-2 border-acid/50 relative scale-105 bg-white/[0.02] flex flex-col justify-between shadow-[0_0_30px_rgba(212,255,0,0.02)]">
                    <div class="absolute top-4 right-6 bg-acid text-black font-black text-[8px] uppercase px-3 py-1 rounded-full tracking-wider">
                        🔥 Самый выгодный
                    </div>
                    <div>
                        <div class="text-4xl font-black italic mb-2 uppercase acid-text">Pro Core</div>
                        <div class="text-xs font-bold text-acid/80 uppercase tracking-wider mb-6">Оптимальный выбор творца</div>
                        <ul class="text-xs space-y-4 mb-12 font-semibold">
                            <li class="flex items-center gap-2">✅ Текст: Все топ-модели + Gemini 2.0 Ultra</li>
                            <li class="flex items-center gap-2">✅ Фото: Высокое качество (Seedream 4.5)</li>
                            <li class="flex items-center gap-2 text-acid">✅ Видео: Kling 3.0 HD Генерации</li>
                            <li class="flex items-center gap-2 text-acid">✅ Аудио: Безлимитный Suno HQ</li>
                            <li class="flex items-center gap-2">✅ Поток: Выделенная высокая скорость</li>
                        </ul>
                    </div>
                    <div>
                        <div class="text-4xl font-black italic mb-8">$39<span class="text-xs text-zinc-500 font-normal"> / месяц</span></div>
                        <button onclick="showAuth('signup')" class="btn-acid w-full py-5 rounded-2xl text-[10px] shadow-lg shadow-acid/10">Купить Pro</button>
                    </div>
                </div>

                <div class="tariff-card glass p-10 rounded-[3rem] border border-white/5 flex flex-col justify-between relative overflow-hidden">
                    <div>
                        <div class="text-4xl font-black italic mb-2 uppercase text-white">Ultra</div>
                        <div class="text-xs font-bold text-zinc-400 uppercase tracking-wider mb-6">Максимальные мощности</div>
                        <ul class="text-xs space-y-4 mb-12 text-zinc-300 font-medium">
                            <li class="flex items-center gap-2">✅ Текст: Полный квантовый приоритет</li>
                            <li class="flex items-center gap-2">✅ Фото: Безлимитный рендеринг 4K</li>
                            <li class="flex items-center gap-2">✅ Видео: Все видео-ядра без ограничений</li>
                            <li class="flex items-center gap-2">✅ Аудио: Мультитрек Suno Stem Export</li>
                            <li class="flex items-center gap-2">✅ Поддержка: Выделенный Enterprise API</li>
                        </ul>
                    </div>
                    <div>
                        <div class="text-4xl font-black italic mb-8">$199</div>
                        <button onclick="showAuth('signup')" class="w-full py-5 border border-zinc-800 hover:border-zinc-700 rounded-2xl text-[10px] font-black uppercase tracking-wider transition">Выбрать</button>
                    </div>
                </div>

            </div>
        </section>

        <section id="integration" class="max-w-7xl mx-auto px-6 py-24 border-t border-white/5 grid md:grid-cols-2 gap-12">
            <div>
                <span class="text-[9px] font-black uppercase tracking-widest acid-text">Интеграции</span>
                <h3 class="text-3xl font-black italic uppercase mt-2 mb-6">Свяжите со своим софтом</h3>
                <p class="text-zinc-500 text-xs leading-relaxed uppercase mb-6">Мы поддерживаем нативную интеграцию с популярными IDE и платформами автоматизации. Получите вебхуки и готовые SDK для работы прямо из коробки.</p>
                <div class="flex flex-wrap gap-3 text-[9px] font-black tracking-widest">
                    <span class="px-4 py-2 bg-white/5 rounded-full border border-white/10">PYTHON SDK</span>
                    <span class="px-4 py-2 bg-white/5 rounded-full border border-white/10">NODEJS EXTENSION</span>
                    <span class="px-4 py-2 bg-white/5 rounded-full border border-white/10">WEBHOOKS v2</span>
                    <span class="px-4 py-2 bg-white/5 rounded-full border border-white/10">REST API MATRICES</span>
                </div>
            </div>
            <div class="glass p-8 rounded-[2rem] border-white/5 flex flex-col justify-between">
                <div>
                    <h4 class="text-sm font-black uppercase mb-2">Техническая поддержка корпораций</h4>
                    <p class="text-xs text-zinc-500 leading-relaxed mb-4">Если вам требуются выделенные локальные сервера (On-Premise) или индивидуальный лимит токенов для больших команд — свяжитесь с нашим корпоративным отделом.</p>
                </div>
                <a href="mailto:enterprise@nexus.ai" class="text-[10px] font-bold uppercase tracking-wider acid-text hover:underline">enterprise@nexus.ai &rarr;</a>
            </div>
        </section>

        <section id="faq" class="max-w-4xl mx-auto px-6 py-24 border-t border-white/5">
            <h2 class="text-3xl font-black italic uppercase mb-10 text-center acid-text">FAQ / Справка</h2>
            <div class="space-y-4">
                <div class="p-6 bg-white/5 rounded-2xl">
                    <div class="text-sm font-bold mb-2">Как работают токены PX?</div>
                    <div class="text-[10px] text-zinc-500 leading-relaxed uppercase">Текст сжигает 50 PX, Изображение 500 PX, Видео/Аудио от 1000 до 5000 PX за генерацию.</div>
                </div>
                <div class="p-6 bg-white/5 rounded-2xl">
                    <div class="text-sm font-bold mb-2">Можно ли отменить подписку Pro Core?</div>
                    <div class="text-[10px] text-zinc-500 leading-relaxed uppercase">Да, вы можете заморозить или отменить подписку в любой момент в настройках личного кабинета без штрафных списаний.</div>
                </div>
            </div>
        </section>

        <footer class="py-20 text-center border-t border-white/5 opacity-30 text-[9px] font-black uppercase tracking-[0.5em]">
            &copy; Nexus AI Quantum Systems 2026
        </footer>
    </div>

    <div id="workspace" class="hidden h-screen flex pt-20 px-4 pb-4 gap-4 overflow-hidden">
        <aside class="w-80 flex flex-col gap-4 h-full">
            <div class="glass rounded-[2rem] p-6 flex flex-col h-full overflow-hidden">
                <div class="bg-white/5 rounded-2xl p-5 mb-6">
                    <div class="flex justify-between text-[9px] font-black acid-text uppercase mb-2"><span>Balance PX</span><span id="token-display">1,000,000</span></div>
                    <div class="w-full bg-white/5 h-1 rounded-full overflow-hidden"><div id="token-bar" class="acid-bg h-full transition-all duration-1000" style="width: 100%"></div></div>
                </div>
                <button onclick="createNewChat()" class="btn-acid w-full py-4 rounded-2xl text-[10px] mb-8">+ NEW STREAM</button>
                <div class="flex-1 overflow-y-auto space-y-2 pr-1" id="chat-history"></div>
            </div>
        </aside>

        <main class="flex-1 flex flex-col gap-4 overflow-hidden">
            <div id="chat-view" class="flex-1 glass rounded-[3rem] p-10 overflow-y-auto space-y-8"></div>
            <div class="h-28 glass rounded-[3rem] p-4 flex gap-4 items-center">
                <div class="flex-1 px-8">
                    <input id="user-input" type="text" class="bg-transparent border-none outline-none text-sm w-full text-white placeholder-zinc-700" placeholder="Введите команду (например, 'сделай из этой фотки тик ток танец')...">
                </div>
                <div class="flex gap-2">
                    <select id="model-select" class="bg-zinc-900 border border-white/10 rounded-2xl text-[9px] px-5 h-14 font-black uppercase outline-none focus:acid-border cursor-pointer">
                        <optgroup label="Text">
                            <option value="gpt">GPT 5.5 Ultra</option>
                            <option value="cloud">Cloud Opus 4.8</option>
                            <option value="gemini">Gemini 2.0 Ultra</option>
                            <option value="deepseek">DeepSeek V3</option>
                        </optgroup>
                        <optgroup label="Image">
                            <option value="banana_pro">Nano Banana Pro</option>
                            <option value="flux">Flux.2 Flex</option>
                            <option value="seedream45">Seedream 4.5</option>
                        </optgroup>
                        <optgroup label="Audio/Video">
                            <option value="kling">Kling 3.0 Video</option>
                            <option value="suno">Suno Music AI</option>
                        </optgroup>
                    </select>
                    <button onclick="sendMessage()" class="btn-acid h-14 px-10 rounded-2xl text-[10px]">Execute</button>
                </div>
            </div>
        </main>
    </div>

    <div id="auth-modal" class="fixed inset-0 z-[100] hidden flex items-center justify-center bg-black/98 backdrop-blur-3xl p-6">
        <div class="w-full max-w-md glass p-10 rounded-[3.5rem] border-t-2 border-white/10 relative">
            <button onclick="hideModal('auth')" class="absolute top-8 right-8 text-zinc-600 hover:text-white transition">✕</button>

            <div id="auth-view-main">
                <div class="flex bg-white/5 rounded-xl p-1 border border-white/5 text-[10px] font-black uppercase tracking-wider mb-8">
                    <button onclick="switchAuthTab('login')" id="tab-btn-login" class="flex-1 py-3 rounded-lg text-center transition-all bg-white/10 text-white">Войти</button>
                    <button onclick="switchAuthTab('signup')" id="tab-btn-signup" class="flex-1 py-3 rounded-lg text-center transition-all text-zinc-500">Регистрация</button>
                </div>

                <div class="grid grid-cols-2 gap-4 mb-6">
                    <button class="bg-white/5 border border-white/10 py-3 rounded-xl text-[9px] font-black tracking-widest hover:bg-white/10 transition uppercase">Google</button>
                    <button class="bg-white/5 border border-white/10 py-3 rounded-xl text-[9px] font-black tracking-widest hover:bg-white/10 transition uppercase">GitHub</button>
                </div>

                <div class="flex flex-col gap-4" id="auth-fields">
                    <input type="text" id="field-name" placeholder="Ваше Имя" class="auth-input hidden fade-in">
                    <input type="text" id="field-username" placeholder="Никнейм (@username)" class="auth-input hidden fade-in">

                    <input type="email" id="field-email" placeholder="Email" class="auth-input">
                    <input type="password" id="field-pass" placeholder="Пароль" class="auth-input">

                    <button onclick="finishAuth()" id="auth-submit-btn" class="btn-acid py-5 rounded-2xl text-xs mt-4">Авторизовать сессию</button>
                </div>
            </div>
        </div>
    </div>

    <div id="image-lightbox" onclick="closeZoomImage()" class="fixed inset-0 z-[150] hidden flex items-center justify-center bg-black/60 backdrop-blur-md p-12 animate-fade-in">
        <div class="relative max-w-5xl max-h-[85vh] rounded-[2rem] overflow-hidden border border-white/10 shadow-2xl bg-zinc-900/30" onclick="event.stopPropagation()">
            <button onclick="closeZoomImage()" class="absolute top-6 right-6 z-20 w-10 h-10 rounded-full bg-black/60 text-white flex items-center justify-center font-bold text-sm hover:bg-white hover:text-black transition shadow-lg">✕</button>

            <div id="lightbox-content-box" class="flex items-center justify-center max-w-full max-h-[85vh]"></div>
        </div>
    </div>

    <script>
        let balance = 1000000;
        let chats = [];
        let currentChatId = null;
        let isLogin = true;

        // Временные маркеры из Python
        const localImageTag = `REPLACE_WITH_IMAGE_TAG`;
        const videoSrcUrl = `REPLACE_WITH_VIDEO_URL`;
        const videoErrorHtml = `REPLACE_WITH_VIDEO_ERROR`;
        const audioSrcUrl = `REPLACE_WITH_AUDIO_URL`;
        const audioErrorHtml = `REPLACE_WITH_AUDIO_ERROR`;

        // --- ФУНКЦИЯ ДИНАМИЧЕСКОГО ПЕРЕКЛЮЧЕНИЯ ВКЛАДОК АВТОРИЗАЦИИ ---
        function switchAuthTab(mode) {
            isLogin = (mode === 'login');

            const loginBtn = document.getElementById('tab-btn-login');
            const signupBtn = document.getElementById('tab-btn-signup');
            const nameField = document.getElementById('field-name');
            const usernameField = document.getElementById('field-username');
            const submitBtn = document.getElementById('auth-submit-btn');

            if (isLogin) {
                loginBtn.className = "flex-1 py-3 rounded-lg text-center transition-all bg-white/10 text-white";
                signupBtn.className = "flex-1 py-3 rounded-lg text-center transition-all text-zinc-500";
                nameField.classList.add('hidden');
                usernameField.classList.add('hidden');
                submitBtn.innerText = "Авторизовать сессию";
            } else {
                loginBtn.className = "flex-1 py-3 rounded-lg text-center transition-all text-zinc-500";
                signupBtn.className = "flex-1 py-3 rounded-lg text-center transition-all bg-white/10 text-white";
                nameField.classList.remove('hidden');
                usernameField.classList.remove('hidden');
                submitBtn.innerText = "Создать квантовый аккаунт";
            }
        }

        function showAuth(mode) { 
            switchAuthTab(mode);
            document.getElementById('auth-modal').classList.remove('hidden'); 
        }

        function hideModal(id) { document.getElementById(id + '-modal').classList.add('hidden'); }

        // --- УЛУЧШЕННЫЕ ФУНКЦИИ ПРОСМОТРА МЕДИА ---

        function zoomMedia(type) {
            const lightbox = document.getElementById('image-lightbox');
            const contentBox = document.getElementById('lightbox-content-box');
            if (!lightbox || !contentBox) return;

            contentBox.innerHTML = ''; 

            if (type === 'image') {
                const originalImg = document.getElementById('nexus-target-img');
                if (!originalImg) return;
                contentBox.innerHTML = `<img src="${originalImg.src}" class="w-auto h-auto max-w-full max-h-[85vh] object-contain">`;
            } else if (type === 'video') {
                const originalVid = document.getElementById('nexus-target-video');
                if (!originalVid) return;
                const source = originalVid.querySelector('source');
                if (!source) return;
                contentBox.innerHTML = `<video controls autoplay loop class="w-auto h-auto max-w-full max-h-[85vh] object-contain rounded-xl"><source src="${source.src}" type="video/mp4"></video>`;
            } else if (type === 'audio') {
                const originalAud = document.getElementById('nexus-target-audio');
                if (!originalAud) return;
                const source = originalAud.querySelector('source');
                if (!source) return;
                contentBox.innerHTML = `
                    <div class="p-12 text-center glass rounded-3xl border border-white/10 max-w-xl w-full flex flex-col items-center gap-6">
                        <div class="w-24 h-24 rounded-full border border-acid/40 flex items-center justify-center animate-pulse bg-acid/5">
                            <span class="text-3xl">🎵</span>
                        </div>
                        <div class="space-y-1">
                            <h4 class="text-xl font-black uppercase italic tracking-wider text-white">NEXUS QUANTUM BEAT</h4>
                            <p class="text-[10px] text-zinc-500 uppercase font-bold tracking-widest">Suno AI Core Engine v.3.5</p>
                        </div>
                        <audio controls autoplay class="w-80 mt-4"><source src="${source.src}" type="audio/mpeg"></audio>
                    </div>
                `;
            }

            lightbox.classList.remove('hidden'); 
        }

        function closeZoomImage() {
            const lightbox = document.getElementById('image-lightbox');
            const contentBox = document.getElementById('lightbox-content-box');
            if (contentBox) contentBox.innerHTML = ''; 
            if (lightbox) lightbox.classList.add('hidden');
        }

        function downloadImage() {
            const img = document.getElementById('nexus-target-img');
            if (!img) return;
            const link = document.createElement('a');
            link.href = img.src;
            link.download = 'nexus_generation_2026.jpg';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }

        function downloadVideo() {
            const vid = document.getElementById('nexus-target-video');
            if (!vid) return;
            const source = vid.querySelector('source');
            if (!source) return;
            const link = document.createElement('a');
            link.href = source.src;
            link.download = 'nexus_dance_2026.mp4';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }

        function downloadAudio() {
            const aud = document.getElementById('nexus-target-audio');
            if (!aud) return;
            const source = aud.querySelector('source');
            if (!source) return;
            const link = document.createElement('a');
            link.href = source.src;
            link.download = 'nexus_quantum_beat_2026.mp3';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }

        function shareImage() {
            const img = document.getElementById('nexus-target-img');
            if (!img) return;
            navigator.clipboard.writeText(img.src).then(() => {
                alert('Квантовая ссылка на изображение скопирована в буфер обмена!');
            }).catch(err => console.error(err));
        }

        function shareVideo() {
            const vid = document.getElementById('nexus-target-video');
            if (!vid) return;
            const source = vid.querySelector('source');
            if (!source) return;
            navigator.clipboard.writeText(window.location.origin + source.getAttribute('src')).then(() => {
                alert('Квантовая ссылка на видео скопирована в буфер обмена!');
            }).catch(err => console.error(err));
        }

        function shareAudio() {
            const aud = document.getElementById('nexus-target-audio');
            if (!aud) return;
            const source = aud.querySelector('source');
            if (!source) return;
            navigator.clipboard.writeText(window.location.origin + source.getAttribute('src')).then(() => {
                alert('Квантовая ссылка на аудио трек скопирована в буфер обмена!');
            }).catch(err => console.error(err));
        }

        // --- БАЗОВАЯ ЛОГИКА ИНТЕРФЕЙСА ---

        function setLang(l) { 
            document.getElementById('lang-ru').className = l === 'ru' ? 'px-3 py-1 rounded-full bg-white/10' : 'px-3 py-1 rounded-full text-zinc-500';
            document.getElementById('lang-en').className = l === 'en' ? 'px-3 py-1 rounded-full bg-white/10' : 'px-3 py-1 rounded-full text-zinc-500';
        }

        function finishAuth() { hideModal('auth'); document.getElementById('landing-page').classList.add('hidden'); document.getElementById('workspace').classList.remove('hidden'); createNewChat(); }

        function createNewChat() {
            const id = Date.now();
            chats.unshift({ id, title: 'New Stream', model: 'N/A', messages: [] });
            currentChatId = id;
            renderHistory();
            renderMessages();
            typeWriter('Quantum core synchronized. Nexus OS 2026 is active.', 'ai');
        }

        function renderHistory() {
            const container = document.getElementById('chat-history');
            container.innerHTML = '';
            chats.forEach(chat => {
                const div = document.createElement('div');
                div.className = `history-card p-5 rounded-2xl cursor-pointer mb-2 ${chat.id === currentChatId ? 'active' : 'bg-white/5'}`;
                div.innerHTML = `
                    <div class="text-[10px] font-black uppercase italic truncate">${chat.title}</div>
                    <div class="text-[8px] acid-text font-bold uppercase mt-1 opacity-60">${chat.model}</div>
                `;
                div.onclick = () => { currentChatId = chat.id; renderMessages(); renderHistory(); };
                container.appendChild(div);
            });
        }

        function renderMessages() {
            const container = document.getElementById('chat-view');
            container.innerHTML = '';
            const chat = chats.find(c => c.id === currentChatId);
            if(!chat) return;
            chat.messages.forEach(msg => {
                appendMessageToUI(msg.role, msg.content, false);
            });
            container.scrollTop = container.scrollHeight;
        }

        function appendMessageToUI(role, content, isNew) {
            const container = document.getElementById('chat-view');
            const isAi = role === 'ai';
            const div = document.createElement('div');
            div.className = `flex ${isAi ? 'justify-start' : 'justify-end'} fade-in mb-8`;
            div.innerHTML = `
                <div class="${isAi ? 'bg-white/5 border border-white/10 text-zinc-200' : 'acid-bg text-black font-bold'} p-8 rounded-[2rem] max-w-[85%] shadow-2xl relative">
                    <p class="text-[8px] font-black uppercase mb-3 tracking-widest opacity-40">${isAi ? 'Nexus System' : 'Operator'}</p>
                    <div class="text-sm leading-loose message-content">${isNew ? '' : content}</div>
                </div>
            `;
            container.appendChild(div);
            container.scrollTop = container.scrollHeight;
            return div.querySelector('.message-content');
        }

        function typeWriter(text, role) {
            const chat = chats.find(c => c.id === currentChatId);
            chat.messages.push({ role, content: text });
            const target = appendMessageToUI(role, text, true);
            let i = 0;
            const interval = setInterval(() => {
                target.innerHTML += text.charAt(i);
                i++;
                if (i >= text.length) clearInterval(interval);
                document.getElementById('chat-view').scrollTop = document.getElementById('chat-view').scrollHeight;
            }, 15);
        }

        function sendMessage() {
            const input = document.getElementById('user-input');
            const modelSelect = document.getElementById('model-select');
            const model = modelSelect.value;
            const modelLabel = modelSelect.options[modelSelect.selectedIndex].text;
            const text = input.value.trim();
            if(!text) return;

            const isVideo = ['kling'].includes(model);
            const isImage = ['banana_pro', 'flux', 'seedream45'].includes(model);
            const isMusic = model === 'suno';
            const cost = isVideo ? 5000 : (isImage ? 500 : (isMusic ? 1000 : 50));

            balance -= cost;
            document.getElementById('token-display').innerText = balance.toLocaleString();
            document.getElementById('token-bar').style.width = (balance / 1000000 * 100) + "%";

            const chat = chats.find(c => c.id === currentChatId);
            chat.messages.push({ role: 'user', content: text });
            if(chat.title === 'New Stream') chat.title = text.substring(0, 25);
            chat.model = modelLabel;

            renderMessages();
            renderHistory();
            input.value = '';

            const container = document.getElementById('chat-view');
            const aiDiv = document.createElement('div');
            aiDiv.className = 'flex justify-start fade-in mb-8';
            aiDiv.innerHTML = `<div class="bg-white/5 border border-white/10 text-zinc-200 p-8 rounded-[2rem] max-w-[85%] shadow-2xl"><div class="text-sm message-content">
                <div class="space-y-4"><div class="text-[9px] font-black uppercase acid-text">Sychronizing Neural Path: ${modelLabel}...</div><div class="gen-loader"><div class="gen-progress"></div></div></div>
            </div></div>`;
            container.appendChild(aiDiv);
            container.scrollTop = container.scrollHeight;

            setTimeout(() => {
                let result = "";
                const low = text.toLowerCase();

                if(low.match(/^(привет|хай|здравствуй)/)) {
                    result = `привет я ${modelLabel}, чем могу помочь?`;
                } 
                else if(isVideo) {
                    if (videoSrcUrl === "") {
                        result = videoErrorHtml;
                    } else {
                        result = `
                        <div class="relative group max-w-md my-2 rounded-2xl overflow-hidden border border-white/10 bg-black/20 shadow-2xl">
                            <video id="nexus-target-video" autoplay loop muted playsinline class="w-full max-h-[450px] object-cover transition duration-300 group-hover:scale-[1.01]">
                                <source src="${videoSrcUrl}" type="video/mp4">
                            </video>

                            <div class="absolute bottom-0 inset-x-0 bg-gradient-to-t from-black/90 via-black/50 to-transparent p-4 flex justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300 z-10">
                                <button onclick="zoomMedia('video')" class="px-3 py-1.5 bg-white/10 hover:bg-white/20 text-white rounded-lg text-[10px] font-bold uppercase tracking-wider backdrop-blur-sm transition">
                                    🔍 Экран
                                </button>
                                <button onclick="downloadVideo()" class="px-3 py-1.5 bg-white/10 hover:bg-white/20 text-white rounded-lg text-[10px] font-bold uppercase tracking-wider backdrop-blur-sm transition">
                                    💾 Скачать
                                </button>
                                <button onclick="shareVideo()" class="px-3 py-1.5 bg-zinc-900/80 hover:bg-white text-zinc-400 hover:text-black rounded-lg text-[10px] font-bold uppercase tracking-wider backdrop-blur-sm transition">
                                    🔗 Ссылка
                                </button>
                            </div>
                        </div>
                        `;
                    }
                }
                else if(low.includes('девушку брюнетку') || low.includes('нарисуй девушку') || low.includes('фотка') || low.includes('картинка')) {
                    result = localImageTag;
                } 
                else if(isMusic) {
                    if (audioSrcUrl === "") {
                        result = audioErrorHtml;
                    } else {
                        result = `
                        <div class="relative group max-w-md my-2 rounded-2xl p-6 border border-white/10 bg-black/40 shadow-2xl flex flex-col gap-4">
                            <div class="flex items-center gap-4">
                                <div class="w-10 h-10 rounded-xl bg-acid/10 border border-acid/30 flex items-center justify-center font-bold text-acid animate-pulse">🎵</div>
                                <div>
                                    <div class="text-xs font-black uppercase italic tracking-wide text-white">Quantum Gen Beat</div>
                                    <div class="text-[8px] text-zinc-500 uppercase tracking-widest font-bold mt-0.5">Core v.3.5 Output</div>
                                </div>
                            </div>

                            <audio id="nexus-target-audio" controls class="w-full mt-2">
                                <source src="${audioSrcUrl}" type="audio/mpeg">
                            </audio>

                            <div class="flex justify-end gap-2 mt-2">
                                <button onclick="zoomMedia('audio')" class="px-3 py-1.5 bg-white/5 hover:bg-white/10 text-white border border-white/5 rounded-lg text-[9px] font-black uppercase tracking-wider transition">
                                    🔍 Экран
                                </button>
                                <button onclick="downloadAudio()" class="px-3 py-1.5 bg-white/5 hover:bg-white/10 text-white border border-white/5 rounded-lg text-[9px] font-black uppercase tracking-wider transition">
                                    💾 Скачать
                                </button>
                                <button onclick="shareAudio()" class="px-3 py-1.5 bg-zinc-900/80 hover:bg-white text-zinc-400 hover:text-black rounded-lg text-[9px] font-black uppercase tracking-wider transition">
                                    🔗 Ссылка
                                </button>
                            </div>
                        </div>
                        `;
                    }
                }
                else {
                    result = `Command processed by ${modelLabel} core. Inference complete.`;
                }

                aiDiv.querySelector('.message-content').innerHTML = result;
                chat.messages.push({ role: 'ai', content: result });
            }, 3000);
        }

        document.getElementById('user-input').addEventListener('keypress', e => e.key === 'Enter' && sendMessage());
    </script>
</body>
</html>
"""


class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Роут для отдачи видеофайла
        if self.path == "/get_video":
            if os.path.exists(video_full_path):
                self.send_response(200)
                self.send_header('Content-type', 'video/mp4')
                self.send_header('Content-Length', str(os.path.getsize(video_full_path)))
                self.end_headers()
                with open(video_full_path, 'rb') as vid_file:
                    self.wfile.write(vid_file.read())
            else:
                self.send_error(404, "Video file not found")
            return

        # Роут для отдачи аудиофайла (бита)
        elif self.path == "/get_beat":
            if os.path.exists(audio_full_path):
                self.send_response(200)
                self.send_header('Content-type', 'audio/mpeg')
                self.send_header('Content-Length', str(os.path.getsize(audio_full_path)))
                self.end_headers()
                with open(audio_full_path, 'rb') as audio_file:
                    self.wfile.write(audio_file.read())
            else:
                self.send_error(404, "Audio file not found")
            return

        # Стандартный роут для загрузки страницы
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()

        # Безопасно внедряем теги и переменные в текст перед отправкой
        final_html = html_code.replace("REPLACE_WITH_IMAGE_TAG", img_tag)
        final_html = final_html.replace("REPLACE_WITH_VIDEO_URL", video_source_url)
        final_html = final_html.replace("REPLACE_WITH_VIDEO_ERROR", video_error_msg)
        final_html = final_html.replace("REPLACE_WITH_AUDIO_URL", audio_source_url)
        final_html = final_html.replace("REPLACE_WITH_AUDIO_ERROR", audio_error_msg)

        self.wfile.write(final_html.encode('utf-8'))


port = 8000
print(f"NEXUS AI v.5.2 Quantum Online: http://localhost:{port}")
server = HTTPServer(('localhost', port), SimpleHandler)
server.serve_forever()