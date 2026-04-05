# Marketplace AI Bot

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3+-green?logo=flask)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Development-orange.svg)](#)

> **Автоматизация ответов на отзывы маркетплейсов**  
> 🛍️ Wildberries • 📦 Ozon • 🚚 Яндекс Маркет

🔗 **Основной сайт:** [автоответыселлер.рф](https://автоответыселлер.рф/)  
🔗 **Демо (разработка):** [1.автоответыселлер.рф](https://1.автоответыселлер.рф/)

---

## 📑 Оглавление

- [🚀 О проекте](#-о-проекта)
- [✨ Возможности](#-возможности)
- [🛠 Технологии](#-технологии)
- [📋 Требования](#-требования)
- [🧪 Локальная разработка](#-локальная-разработка)
- [☁️ Деплой на Beget](#️-деплой-на-beget)
- [🔒 SEO для поддомена](#-seo-для-поддомена-разработки)
- [📁 Структура проекта](#-структура-проекта)
- [📡 Эндпоинты](#-эндпоинты)
- [🧪 Статус разработки](#-статус-разработки)
- [🛡️ Безопасность](#️-безопасность)
- [👮 Админка для предложений](#-админка-для-предложений)
- [🆘 Устранение неполадок](#-устранение-неполадок)
- [🤝 Вклад в проект](#-вклад-в-проект)
- [📄 Лицензия](#-лицензия)

---

## 🚀 О проекте

**Marketplace AI Bot** — это веб-приложение на Flask для автоматизации работы с отзывами покупателей на российских маркетплейсах. Приложение помогает селлерам быстро генерировать вежливые, релевантные и персонализированные ответы с использованием нейросетей.

### 🎯 Зачем это нужно?

| Проблема | Решение |
|----------|---------|
| ⏱️ Много времени на ручные ответы | 🤖 Автоматическая генерация ответов |
| 📊 Отзывы в разных кабинетах | 🔄 Единый дашборд для всех маркетплейсов |
| 😤 Сложно сохранять тон бренда | 🎨 Шаблоны и настройки стиля ответов |
| 📈 Нет аналитики по обратной связи | 📊 История ответов и статистика |

---

## ✨ Возможности

- 🔐 Регистрация и авторизация пользователей
- 📊 Личный кабинет с дашбордом активности
- 🔑 Управление API-ключами для Wildberries, Ozon, Яндекс Маркет
- 📥 Получение списка отзывов через API маркетплейсов
- 🤖 Генерация ответов с помощью LLM (OpenRouter) — *в разработке*
- 📚 База знаний с шаблонами типовых ответов
- 📝 Блог со статьями по работе с отзывами
- 👤 Профиль пользователя с настройками
- 🔒 Защита поддомена разработки от индексации (`noindex`, `canonical`)
- 🌐 Адаптивный интерфейс (Bootstrap 5)

---

## 🛠 Технологии

### Бэкенд
```
Python 3.10+
├── Flask 2.3+
├── Flask-SQLAlchemy
├── Flask-Login
├── Flask-WTF
├── python-dotenv
└── requests
```

### Фронтенд
- HTML5 + Jinja2 шаблоны
- CSS3 (Bootstrap 5, кастомные стили)
- Минимальный JavaScript для интерактива

### Инфраструктура
| Компонент | Технология |
|-----------|-----------|
| **Хостинг** | Beget (Ubuntu 22.04, Docker) |
| **Веб-сервер** | Apache + Passenger |
| **База данных** | SQLite (готово к миграции на PostgreSQL) |
| **Контроль версий** | Git + GitHub (SSH) |
| **Окружение** | Python venv + `.env` конфигурация |

### Интеграции (в процессе)
- 🛍️ Wildberries API
- 📦 Ozon API  
- 🚚 Яндекс Маркет API
- 🧠 OpenRouter (LLM)

---

## 📋 Требования

### Для локальной разработки
- Python 3.10 или выше
- pip (менеджер пакетов Python)
- Git
- Виртуальное окружение (`venv` или `virtualenv`)

### Для деплоя на Beget
- Аккаунт на [beget.com](https://beget.com)
- Доступ к панели управления хостингом
- Настроенный домен/поддомен
- Поддержка Python 3.10+ и Passenger

---

## 🧪 Локальная разработка

### 1. Клонирование репозитория
```bash
git clone https://github.com/<username>/marketplace-ai-bot.git
cd marketplace-ai-bot
```

### 2. Создание виртуального окружения
```bash
# Linux / macOS
python -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Установка зависимостей
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Настройка конфигурации

```bash
# Скопируйте пример файла переменных окружения
cp .env.example .env

# Отредактируйте .env и установите ваши значения
# SECRET_KEY, DATABASE_URL, FLASK_ENV
```

> ⚠️ **Важно:** `SECRET_KEY` должен быть уникальным и минимум 32 символа. Никогда не коммитьте `.env` в репозиторий!

### 5. Инициализация миграций базы данных

Для управления миграциями используется Flask-Migrate (Alembic).

```bash
# Инициализация миграций (выполняется один раз)
flask db init

# Создание первой миграции
flask db migrate -m "Initial migration"

# Применение миграций к базе данных
flask db upgrade
```

> 💡 **Примечание:** При использовании SQLite база данных будет создана автоматически при первом запуске миграций.

### 6. Проверка подключения к базе данных

При запуске приложения в консоли вы увидите сообщение о типе подключённой БД и текущей конфигурации:

```
✅ Подключено к SQLite
🔧 Конфигурация: Development
```

Или для MySQL на Beget:

```
✅ Подключено к MySQL 8.0 (Beget)
🔧 Конфигурация: Production
```

### 7. Запуск приложения
```bash
# Режим разработки
flask run

# Или напрямую
python app.py
```

🌐 Приложение будет доступно по адресу: **http://127.0.0.1:5000/**

---

## ☁️ Деплой на Beget (Apache + Passenger)



### 🔄 Процесс деплоя (кратко)

```mermaid
graph LR
    A[Код в GitHub] --> B[SSH на сервер]
    B --> C[git pull]
    C --> D[pip install -r requirements.txt]
    D --> E[touch tmp/restart.txt]
    E --> F[✅ Приложение обновлено]
```

### 🧹 Чистая установка: пошаговая инструкция

> ⚠️ Все команды выполняются **после входа в Docker-контейнер** на Beget:  
> `ssh user@user.beget.tech` → `ssh localhost -p222`

#### 🔹 Шаг 0: Подготовка
```bash
# Перейдите в директорию проекта
cd ~/public_html

# (Опционально) Очистите папку, если начинается с нуля
rm -rf * .[^.]* 2>/dev/null
ls -la  # Должно показать только . и ..
```

#### 🔹 Шаг 1: Клонирование репозитория
```bash
git clone https://github.com/<username>/marketplace-ai-bot.git .
ls -la  # Проверьте, что файлы появились
```

#### 🔹 Шаг 2: Виртуальное окружение
```bash
# Создайте venv
python3 -m venv venv

# Активируйте
source venv/bin/activate

# Проверьте активацию
which python
# Ожидаем: /home/.../public_html/venv/bin/python
```

#### 🔹 Шаг 3: Зависимости
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 🔹 Шаг 4: Конфигурация

```bash
# Создайте .env с безопасным ключом и настройками для MySQL
cat > .env << EOF
SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
DATABASE_URL=mysql+pymysql://username:password@hostname/database_name?charset=utf8mb4
FLASK_ENV=production
EOF

# Замените username, password, hostname, database_name на ваши данные от БД Beget
# Данные от MySQL можно найти в панели управления Beget -> Базы данных

# Создайте необходимые папки
mkdir -p tmp instance
```

> 💡 **Важно для Beget:**  
> - Получите данные от MySQL в панели управления: `Базы данных` → ваша БД → `Параметры подключения`  
> - Формат DATABASE_URL: `mysql+pymysql://user:pass@db.beget.com/dbname?charset=utf8mb4`

#### 🔹 Шаг 5: Инициализация базы данных (миграции)

```bash
# Инициализация миграций (только один раз при первом деплое)
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# При последующих обновлениях достаточно только:
# flask db upgrade
```

#### 🔹 Шаг 6: Проверка и запуск
```bash
# Проверьте импорт приложения
python -c "from app import app; print('✅ OK:', app.name)"

# Инициализируйте БД
python -c "from app import app, db; app.app_context().push(); db.create_all()"

# Перезагрузите Passenger
touch tmp/restart.txt

# Подождите и проверьте
sleep 10
curl -s https://ваш-поддомен.рф/ping
# Ожидаем: pong
```

✅ **Готово!** Приложение работает.

---

### ⚙️ Файлы конфигурации (шаблоны)

#### `passenger_wsgi.py`
```python
# -*- coding: utf-8 -*-
import sys
import os

# Укажите актуальный путь к проекту
PROJECT_ROOT = '/home/<user>/public_html'
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Укажите путь к site-packages вашего venv
VENV_SITE = f'{PROJECT_ROOT}/venv/lib/python3.10/site-packages'
if VENV_SITE not in sys.path:
    sys.path.insert(1, VENV_SITE)

os.chdir(PROJECT_ROOT)

# Обязательно: переменная должна называться 'application'
from app import app as application
```

#### `.htaccess`
```apache
PassengerEnabled On
PassengerAppRoot /home/<user>/public_html
PassengerPython /home/<user>/public_html/venv/bin/python3

# Опционально: кэширование статических файлов
<IfModule mod_expires.c>
    ExpiresActive On
    ExpiresByType image/jpg "access plus 1 year"
    ExpiresByType image/jpeg "access plus 1 year"
    ExpiresByType image/png "access plus 1 year"
    ExpiresByType text/css "access plus 1 month"
    ExpiresByType application/javascript "access plus 1 month"
</IfModule>
```

---

## 🔒 SEO для поддомена разработки

###  `robots.txt`
```txt
User-agent: *
Disallow: /

# Разрешаем мониторинг
User-agent: UptimeRobot
Allow: /ping

Sitemap: https://основной-домен.рф/sitemap.xml
```

### 🏷️ Мета-теги в `base.html`
```html
{% if request.host.startswith('1.') or request.host.startswith('bot.') %}
<meta name="robots" content="noindex, nofollow">
<link rel="canonical" href="https://основной-домен.рф{{ request.path }}">
{% endif %}
```

### ⚠️ Визуальный индикатор
На поддоменах разработки автоматически отображается баннер:
> ⚠️ Это версия для разработки. Основной сайт: [основной-домен.рф](#)

---

## 📁 Структура проекта

```
marketplace-ai-bot/
├── .env                      # Секреты (НЕ в Git)
├── .gitignore                # Правила игнорирования
├── .htaccess                 # Конфигурация Apache/Passenger
├── app.py                    # Основное Flask-приложение
├── models.py                 # Модели SQLAlchemy
├── requirements.txt          # Зависимости Python
├── passenger_wsgi.py         # Точка входа для Passenger
├── robots.txt                # SEO-конфигурация
├── deploy.sh                 # Скрипт автоматизации деплоя
│
├── instance/
│   └── users.db              # База данных SQLite
│
├── static/
│   ├── css/
│   │   ├── style.css         # Основные стили
│   │   └── components.css    # Переиспользуемые компоненты
│   ├── images/               # Логотипы, иконки
│   ├── avatars/              # Загруженные аватары
│   └── favicon.ico
│
├── templates/
│   ├── base.html             # Базовый шаблон с SEO-тегами
│   ├── index.html            # Главная
│   ├── login.html            # Вход
│   ├── register.html         # Регистрация
│   ├── dashboard.html        # Дашборд
│   ├── profile.html          # Профиль
│   ├── knowledge_base.html   # База знаний
│   ├── privacy.html          # Политика конфиденциальности
│   ├── offer.html            # Оферта
│   ├── progress.html         # Статус разработки
│   └── blog/                 # Статьи
│       └── *.html
│
├── tmp/
│   └── restart.txt           # Триггер перезагрузки Passenger
│
├── utils/
│   ├── wb_api.py             # Wildberries API
│   ├── ozon_api.py           # Ozon API
│   └── yandex_api.py         # Яндекс Маркет API
│
└── venv/                     # Виртуальное окружение (НЕ в Git)
```

---

## 📡 Эндпоинты

| Эндпоинт | Метод | Описание | Доступ |
|----------|-------|----------|--------|
| `/` | GET | Главная страница | Публичный |
| `/ping` | GET | Health check | Публичный |
| `/login` | GET, POST | Форма входа | Публичный |
| `/register` | GET, POST | Регистрация | Публичный |
| `/logout` | GET | Выход из системы | Авторизованный |
| `/dashboard` | GET | Личный кабинет | 🔐 Авторизованный |
| `/profile` | GET, POST | Управление профилем | 🔐 Авторизованный |
| `/add-api-key` | POST | Добавление API-ключа | 🔐 Авторизованный |
| `/delete-api-key/<int:key_id>` | POST | Удаление API-ключа | 🔐 Авторизованный |
| `/generate-reply` | POST | Генерация ответа (заглушка) | 🔐 Авторизованный |
| `/knowledge-base` | GET, POST | База знаний | 🔐 Авторизованный |
| `/blog/<slug>` | GET | Статья блога | Публичный |
| `/robots.txt` | GET | SEO-конфигурация | Публичный |

> 🔐 — требуется авторизация

---

## 🧪 Статус разработки

```mermaid
graph LR
    A[✅ Ядро Flask] --> B[✅ Аутентификация]
    B --> C[✅ Профиль пользователя]
    C --> D[🔄 API маркетплейсов]
    D --> E[⏳ LLM-генерация]
    E --> F[⏳ Автоотправка]
    F --> G[⏳ Аналитика]
```

| Функция | Статус | Примечание |
|---------|--------|-----------|
| 🔐 Регистрация / вход | ✅ Готово | С хешированием паролей |
| 👤 Профиль пользователя | ✅ Готово | Редактирование, аватар |
| 🔑 Управление API-ключами | ✅ Готово | Шифрование в БД |
| 🛍️ Wildberries API | 🔄 В работе | Получение отзывов |
| 📦 Ozon API | ⏳ Запланировано |  |
| 🚚 Яндекс Маркет API | ⏳ Запланировано |  |
| 🤖 Генерация ответов (LLM) | ⏳ В разработке | Через OpenRouter |
| 📤 Автоотправка ответов | ⏳ Запланировано |  |
| 📊 Аналитика отзывов | ⏳ Запланировано |  |
| 🌐 Мультиязычность | ⏳ Запланировано |  |

---

## 🛡️ Безопасность

### ✅ Реализовано
- Хеширование паролей через `Werkzeug.security.generate_password_hash`
- Защита сессий с `SECRET_KEY` из `.env`
- Ограничение доступа к маршрутам через `@login_required`
- Валидация входных данных на бэкенде
- Экранирование вывода в шаблонах Jinja2 (защита от XSS)

### 🔐 Рекомендации для продакшена
1. **Никогда не коммитьте `.env`** — добавьте его в `.gitignore`
2. **Регулярно обновляйте зависимости**:  
   ```bash
   pip list --outdated
   pip install --upgrade -r requirements.txt
   ```
3. **Используйте HTTPS** — на Beget включён по умолчанию
4. **Мониторьте логи**: `~/logs/public_html/error.log`
5. **Ограничьте доступ к админ-маршрутам** по IP при необходимости

### 🔑 Генерация безопасного SECRET_KEY
```bash
python -c 'import secrets; print(secrets.token_hex(32))'
# Пример вывода: a3f8b2c1d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0
```

---

## 🔐 Безопасность формы (Шаг 3)

### Защита от XSS

- Весь пользовательский ввод проходит санитизацию перед сохранением в базу данных.
- Специальные символы (`<`, `>`, `&`, `"`, `'`) экранируются с помощью `html.escape()`.
- Длина текста предложения ограничена 2000 символов.
- Пустые или невалидные данные отклоняются с понятным сообщением об ошибке.

### Лимит отправки (Rate Limiting)

- Максимум **3 предложения в час** с одного авторизованного пользователя.
- Проверка осуществляется по `user_id` через подсчёт записей в таблице `Suggestion` за последний час.
- При превышении лимита возвращается ошибка HTTP 429 с сообщением:  
  *"Вы отправили слишком много предложений. Пожалуйста, подождите час перед следующей отправкой."*
- Для анонимных пользователей лимит пока не применяется (требуется доработка БД).

### CSRF-заглушка (для беты)

- Реализована проверка заголовка `Referer` на совпадение с доменом приложения.
- Запросы с внешних доменов блокируются с ошибкой HTTP 403.
- ⚠️ **Внимание:** Перед публичным запуском рекомендуется заменить эту заглушку на полноценную CSRF-защиту через расширение `Flask-WTF`.

### Логирование подозрительных действий

Все попытки нарушения безопасности фиксируются в логах:
- `CSRF check failed: Referer=..., Host=..., IP=...` — при блокировке по Referer
- `Rate limit hit: user_id=..., count=..., IP=...` — при превышении лимита
- `Invalid input from user_id=...: ...` — при попытке отправить невалидный текст

### Тестирование безопасности

Вы можете протестировать защиту локально с помощью `curl`:

**1. Проверка санитизации (XSS):**
```bash
curl -X POST http://127.0.0.1:5000/api/suggestion \
  -H "Content-Type: application/json" \
  -H "Referer: http://127.0.0.1:5000/" \
  -d '{"text": "<script>alert(1)</script>"}'
# Текст должен сохраниться в БД как: &lt;script&gt;alert(1)&lt;/script&gt;
```

**2. Проверка лимита (429 Too Many Requests):**
Отправьте 4 запроса подряд быстро (после авторизации). Четвёртый должен вернуть ошибку:
```json
{"error": "Вы отправили слишком много предложений. Пожалуйста, подождите час перед следующей отправкой."}
```

**3. Проверка Referer (403 Forbidden):**
```bash
curl -X POST http://127.0.0.1:5000/api/suggestion \
  -H "Referer: https://evil.com" \
  -H "Content-Type: application/json" \
  -d '{"text": "Тест"}'
# Должен вернуть ошибку 403: "Запрос отклонён по соображениям безопасности..."
```

---

## 👮 Админка для предложений

### Доступ к админ-панели

1. Перейдите на страницу `/admin/suggestions`
2. Введите пароль из переменной окружения `ADMIN_PASSWORD`
3. После успешного входа сессия сохраняется на 24 часа

### Функции админки

- 📋 Просмотр всех предложений пользователей с пагинацией (50 записей на страницу)
- 📥 Экспорт в CSV (кнопка вверху страницы) — файл в формате UTF-8 с BOM для Excel
- 🔍 Сортировка по дате (новые предложения сверху)
- 📊 Отображение email пользователя, даты и текста предложения

### Первый вход и настройка прав администратора

Для предоставления прав администратора конкретному пользователю через базу данных:

```bash
flask shell
>>> from app import db
>>> from models import User
>>> user = User.query.filter_by(email='your@email.com').first()
>>> user.is_admin = True
>>> db.session.commit()
>>> exit()
```

### Переменные окружения для админки

Добавьте в файл `.env`:

```bash
# Пароль для доступа к админ-панели
ADMIN_PASSWORD=change_this_in_production
```

⚠️ **Важно:** В production обязательно измените пароль на сложный!

### Логи админ-панели

Все действия администратора логируются:
- Вход в админку: `✅ Вход в админку выполнен`
- Просмотр предложений: `📋 Админ просмотрел предложения: страница N`
- Экспорт CSV: `📥 CSV экспортирован пользователем admin`
- Выход из админки: `🚪 Выход из админки`

---

## 🚀 Деплой на Beget (пошагово)

### 1. Подготовка базы данных

1. В панели Beget → раздел "MySQL" → создать базу данных
2. Создать пользователя БД и надёжный пароль
3. Записать параметры: `host`, `database_name`, `username`, `password`

### 2. Загрузка файлов на хостинг

1. Подключиться по FTP (данные из панели Beget)
2. Загрузить **все файлы проекта** в папку сайта
3. **НЕ загружать:** `.env`, `venv/`, `.git/`, `__pycache__/`, `*.pyc`, `logs/`, `instance/`

### 3. Настройка переменных окружения

В панели Beget → "Сайты" → "Переменные окружения" добавить:

```bash
# 🔐 Безопасность (ОБЯЗАТЕЛЬНО сменить!)
SECRET_KEY=ваш_секретный_ключ_минимум_32_символа
ADMIN_PASSWORD=надёжный_пароль_для_админки

# 🗄️ База данных (MySQL 8.0)
DATABASE_URL=mysql+pymysql://username:password@host/database_name?charset=utf8mb4

# ⚙️ Окружение
FLASK_ENV=production
FLASK_APP=app.py
```

> 💡 Сгенерировать SECRET_KEY: `python -c "import secrets; print(secrets.token_hex(32))"`

### 4. Установка зависимостей

1. В панели Beget → "Python" → выбрать Python 3.10+
2. Через SSH или терминал хостинга выполнить:
   ```bash
   cd /home/username/site_folder
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

### 5. Миграции базы данных

```bash
source venv/bin/activate
flask db upgrade
```

### 6. Создание первого администратора

```bash
python scripts/create_first_admin.py ваш@email.com
```

### 7. Проверка работы

1. Открыть сайт в браузере
2. Проверить: регистрация, вход, отправка предложения
3. Проверить админку: `/admin/suggestions`
4. Проверить логи: файл `logs/app.log`

---

## 📋 Чек-лист перед запуском бета-теста

- [ ] БД MySQL создана и подключена
- [ ] Все переменные окружения заданы на Beget
- [ ] Миграции применены (`flask db upgrade`)
- [ ] Сайт открывается по HTTPS
- [ ] Регистрация работает
- [ ] Вход/выход работают
- [ ] Отправка предложений работает
- [ ] Админка доступна только по паролю
- [ ] Экспорт CSV работает
- [ ] Логи пишутся в `logs/app.log`
- [ ] Страницы 404/500 отображаются корректно
- [ ] Скрипт `create_first_admin.py` работает

---

## 🆘 Устранение неполадок

### ❌ Приложение не запускается / 500 ошибка

```bash
# 1. Проверьте логи Passenger
tail -f ~/logs/public_html/error.log

# 2. Проверьте синтаксис Python
python -m py_compile app.py

# 3. Проверьте импорт приложения
python -c "from app import app; print('OK')"
```

### ❌ Ошибка `ModuleNotFoundError`

```bash
# Убедитесь, что venv активен:
# В строке приглашения должно быть: (venv)

# Если нет — активируйте:
source venv/bin/activate

# Переустановите зависимости:
pip install -r requirements.txt
```

### ❌ Passenger не перезагружается

```bash
# 1. Убедитесь, что файл существует
touch tmp/restart.txt

# 2. Проверьте права на папку
chmod 755 tmp

# 3. Альтернатива: перезагрузите приложение в панели хостинга
```

### ❌ `git pull` не работает (ошибка аутентификации)

```bash
# Проверьте SSH-ключ:
ssh -T git@github.com

# Если ключ не добавлен в сессию:
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/github

# Убедитесь, что remote настроен на SSH:
git remote -v
# Должно быть: git@github.com:<username>/marketplace-ai-bot.git
```

### ❌ Ошибка `getcwd: cannot access parent directories`

```bash
# Выйдите и подключитесь заново:
exit
ssh user@user.beget.tech
ssh localhost -p222

# Явно укажите путь:
cd ~/public_html
```

---

## 🤝 Вклад в проект

Приветствуется любая помощь! 🙌

### Как предложить изменения:
1. Создайте **Issue** с описанием идеи или бага
2. Форкните репозиторий
3. Создайте ветку для фичи:  
   ```bash
   git checkout -b feature/название-фичи
   ```
4. Внесите изменения и закоммитьте:  
   ```bash
   git commit -m "feat: краткое описание изменений"
   ```
5. Запушьте и откройте **Pull Request**

### 📐 Соглашения по коду
- 🐍 Используйте `snake_case` для переменных и функций
- 📝 Документируйте сложные функции через docstrings
- 🇷🇺 Бизнес-логику комментируйте на русском
- ✅ Проверяйте код перед коммитом:  
  ```bash
  python -m flake8 app.py  # при наличии flake8
  ```

---

## 📄 Лицензия

Проект распространяется под лицензией **MIT**.  
Подробнее см. файл [LICENSE](LICENSE).

```
MIT License

Copyright (c) 2026

Permission is hereby granted...
```

> ⚠️ При использовании кода в коммерческих проектах укажите ссылку на оригинальный репозиторий.

---

## 📞 Контакты и поддержка

- 🐛 **Баги и предложения:** [Issues](https://github.com/<username>/marketplace-ai-bot/issues)
- 💬 **Вопросы:** создайте обсуждение в репозитории
- 🌐 **Сайт проекта:** [автоответыселлер.рф](https://автоответыселлер.рф/)

---

> 🔄 **Последнее обновление:** 30 марта 2026 г.  
> 🐳 **Развёрнуто на:** Beget (Docker) • Python 3.10 • Flask • Passenger

<p align="center">
  <sub>Сделано с ❤️ для селлеров маркетплейсов</sub>
</p>
