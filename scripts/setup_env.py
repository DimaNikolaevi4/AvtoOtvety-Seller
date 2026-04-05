#!/usr/bin/env python3
"""
🔧 setup_env.py — Мастер настройки .env для Beget

Автоматически создаёт файл .env с:
- Параметрами БД (вы вводите)
- Сгенерированными ключами безопасности
- Правильно экранированной DATABASE_URL
"""

import os
import secrets
from urllib.parse import quote_plus

def get_input(prompt: str, default: str = None, secure: bool = False) -> str:
    """Запрос ввода с поддержкой значения по умолчанию"""
    if default:
        full_prompt = f"{prompt} [{default}]: "
    else:
        full_prompt = f"{prompt}: "
    
    try:
        value = input(full_prompt).strip()
        return value if value else default
    except EOFError:
        # При автоматическом тестировании или piped input
        return default

def main():
    print("🚀 === Настройка .env для marketplace-ai-bot ===\n")
    
    # === 1. Параметры БД ===
    print("📦 1. НАСТРОЙКИ БАЗЫ ДАННЫХ")
    print("-" * 40)
    
    db_user = get_input("DB_USER (пользователь БД)", default="your_db_user")
    db_pass = get_input("DB_PASS (пароль БД)", secure=True)
    
    if not db_pass:
        print("❌ Пароль БД обязателен!")
        return
    
    db_host = get_input("DB_HOST", default="localhost")
    db_name = get_input("DB_NAME (имя БД)", default=db_user)
    db_port = get_input("DB_PORT", default="3306")
    
    # === 2. Безопасность (авто-генерация) ===
    print("\n🔐 2. БЕЗОПАСНОСТЬ (автоматическая генерация)")
    print("-" * 40)
    
    secret_key = secrets.token_hex(32)
    admin_password = secrets.token_urlsafe(16)
    
    print(f"SECRET_KEY: {secret_key}")
    print(f"ADMIN_PASSWORD: {admin_password}")
    
    # === 3. Режим ===
    print("\n⚙️ 3. РЕЖИМ РАБОТЫ")
    print("-" * 40)
    
    flask_env = get_input("FLASK_ENV", default="production")
    debug = get_input("DEBUG (True/False)", default="False")
    
    # === 4. Формирование DATABASE_URL ===
    print("\n🔗 4. Генерация DATABASE_URL")
    print("-" * 40)
    
    encoded_pass = quote_plus(db_pass)
    database_url = (
        f"mysql+pymysql://{db_user}:{encoded_pass}@{db_host}:{db_port}/{db_name}"
        f"?charset=utf8mb4"
    )
    
    print(f"DATABASE_URL: {database_url}")
    print("✅ Пароль автоматически экранирован (special chars → %XX)")
    
    # === 5. Запись в файл ===
    print("\n💾 5. Сохранение в .env")
    print("-" * 40)
    
    env_content = f'''# === 🗄️ БАЗА ДАННЫХ ===
DB_USER="{db_user}"
DB_PASS="{db_pass}"
DB_HOST="{db_host}"
DB_NAME="{db_name}"
DB_PORT={db_port}

# === 🔐 БЕЗОПАСНОСТЬ ===
SECRET_KEY="{secret_key}"
ADMIN_PASSWORD="{admin_password}"

# === ⚙️ РЕЖИМ ===
FLASK_ENV="{flask_env}"
DEBUG={debug}

# === 📡 АВТО-ГЕНЕРАЦИЯ: Строка подключения ===
# Не редактируйте вручную! Пересоздайте через setup_env.py при изменении пароля
DATABASE_URL="{database_url}"
'''
    
    env_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
        '.env'
    )
    
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print(f"✅ Файл .env создан: {env_path}")
    
    # === 6. Проверка прав доступа ===
    os.chmod(env_path, 0o600)  # Только владелец может читать/писать
    print("🔒 Установлены права доступа 600 (только чтение для владельца)")
    
    # === 7. Итог ===
    print("\n" + "=" * 50)
    print("🎉 ГОТОВО! Следующие шаги:")
    print("=" * 50)
    print("1. Проверьте файл .env (особенно пароль БД)")
    print("2. Примените миграции: flask db upgrade")
    print("3. Перезапустите Passenger: touch tmp/restart.txt")
    print("4. Проверьте: curl -k https://ваш-домен/ping")
    print("\n⚠️  ВАЖНО: Не коммитьте .env в Git! Он уже в .gitignore")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Прервано пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
