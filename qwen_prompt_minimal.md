# 🚀 Краткий промпт: Деплой marketplace-ai-bot на Beget (Passenger + MySQL)

## ⚠️ ГЛАВНОЕ ПРАВИЛО
**Passenger НЕ читает `.env` автоматически**. Загружайте `.env` в `passenger_wsgi.py` **ПЕРЕД** `from app import app`.

---

## 🔧 Обязательные изменения

### 1. `passenger_wsgi.py` (критично!)
```python
import sys, os
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path: sys.path.insert(0, PROJECT_ROOT)
venv_site = os.path.join(PROJECT_ROOT, 'venv', 'lib', 'python3.10', 'site-packages')
if os.path.isdir(venv_site) and venv_site not in sys.path: sys.path.insert(0, venv_site)

# 🔥 КРИТИЧНО: Загружаем .env ДО импорта app
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(PROJECT_ROOT, '.env'))
except ImportError: pass

from app import app as application
```

### 2. `app.py` — Безопасная проверка DATABASE_URL
```python
from dotenv import load_dotenv
load_dotenv()  # Безопасно вызывать повторно

db_uri = os.environ.get('DATABASE_URL') or app.config.get('SQLALCHEMY_DATABASE_URI')
if not db_uri:
    raise RuntimeError("DATABASE_URL is required")
if db_uri.startswith('sqlite'):  # ✅ Теперь безопасно
    # ... логика для SQLite
```

### 3. `config.py` — URL-encoding пароля
```python
from urllib.parse import quote_plus
def build_mysql_url(user, password, host, database, port=3306):
    return f"mysql+pymysql://{user}:{quote_plus(password)}@{host}:{port}/{database}?charset=utf8mb4"

class Config:
    if os.getenv('DB_USER') and os.getenv('DB_PASS'):
        SQLALCHEMY_DATABASE_URI = build_mysql_url(
            os.getenv('DB_USER'), os.getenv('DB_PASS'),
            os.getenv('DB_HOST', '127.0.0.1'),
            os.getenv('DB_NAME'), int(os.getenv('DB_PORT', 3306))
        )
    else:
        SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
```

### 4. `.env.example` (минимум)
```dotenv
DATABASE_URL=mysql+pymysql://user:pass@127.0.0.1/dbname?charset=utf8mb4
SECRET_KEY=change_me  # python -c "import secrets; print(secrets.token_hex(32))"
ADMIN_PASSWORD=change_me
FLASK_ENV=production
DEBUG=False
```

### 5. Эндпоинты мониторинга (в `app.py`)
```python
@app.route('/health')
def health_check():
    return {'status': 'ok'}, 200

@app.route('/ready')
def readiness_check():
    try:
        with db.engine.connect() as conn:
            conn.execute(db.text('SELECT 1'))
        return {'status': 'ready'}, 200
    except Exception as e:
        return {'status': 'not_ready', 'error': str(e)}, 503
```

---

## ✅ Критерии приёмки
- [ ] `passenger_wsgi.py` загружает `.env` **до** импорта `app`
- [ ] Проверка `DATABASE_URL`: `if db_uri and db_uri.startswith(...)`
- [ ] Пароль БД экранируется через `quote_plus()`
- [ ] Приложение не падает без `.env` (понятная ошибка)
- [ ] Работает локально (`flask run`) и на Passenger

---

## 📝 README.md — Добавить предупреждение
> ⚠️ **Не упрощайте `passenger_wsgi.py`!** Загрузка `.env` перед импортом `app` критична для Passenger.

## 🚀 Быстрый деплой
```bash
ssh user@user.beget.tech && ssh localhost -p222
cd ~/site/public_html && git pull
source venv/bin/activate && pip install -r requirements.txt
mkdir -p tmp && touch tmp/restart.txt  # Перезапуск Passenger
curl -k https://your-domain.ru/ping  # Ожидаем: pong
```

---

**Сохранить обратную совместимость**: Локально (`flask run`), VPS/Docker, Passenger.
