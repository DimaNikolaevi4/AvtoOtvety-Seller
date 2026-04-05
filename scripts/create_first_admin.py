#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Скрипт для создания первого администратора.

Использование:
    python scripts/create_first_admin.py email@domain.com

Пример:
    python scripts/create_first_admin.py admin@example.com
"""
import sys
import os

# Добавляем корень проекта в путь для импортов
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import db, User


def create_first_admin(email):
    """Назначает пользователя с указанным email администратором."""
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        
        if not user:
            print(f"❌ Пользователь с email '{email}' не найден в базе данных.")
            print("💡 Сначала зарегистрируйтесь через сайт: /register")
            return False
        
        if user.is_admin:
            print(f"ℹ️  Пользователь '{email}' уже является администратором.")
            return True
        
        user.is_admin = True
        db.session.commit()
        
        print(f"✅ Пользователь '{email}' успешно назначен администратором!")
        print("🔑 Теперь вы можете войти в админку: /admin/suggestions")
        return True


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("❌ Ошибка: Не указан email пользователя.")
        print("\nИспользование:")
        print("    python scripts/create_first_admin.py email@domain.com")
        print("\nПример:")
        print("    python scripts/create_first_admin.py admin@example.com")
        sys.exit(1)
    
    email = sys.argv[1]
    
    # Простая валидация email
    if '@' not in email or '.' not in email.split('@')[-1]:
        print(f"❌ Ошибка: Некорректный формат email '{email}'")
        sys.exit(1)
    
    success = create_first_admin(email)
    sys.exit(0 if success else 1)
