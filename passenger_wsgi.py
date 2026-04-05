# -*- coding: utf-8 -*-
"""
Точка входа для Passenger (Beget)
⚠️ Beget требует, чтобы переменная называлась 'application'
"""
import sys
import os

# Автоматическое определение корневой директории проекта
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Добавляем корень проекта в путь
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Автоматическая активация виртуального окружения
venv_path = os.path.join(PROJECT_ROOT, 'venv')
if os.path.exists(venv_path):
    # Находим site-packages динамически (независимо от версии Python)
    for root, dirs, files in os.walk(venv_path):
        if 'site-packages' in dirs:
            site_packages = os.path.join(root, 'site-packages')
            if site_packages not in sys.path:
                sys.path.insert(0, site_packages)
            break
    
    # Добавляем путь к python исполняемому файлу в PATH
    venv_bin = os.path.join(venv_path, 'bin')
    if os.path.exists(venv_bin):
        os.environ['PATH'] = venv_bin + os.pathsep + os.environ.get('PATH', '')

# Импортируем приложение из app.py
from app import app as application

# Отключаем debug режим для продакшена
application.debug = False

if __name__ == '__main__':
    application.run()
