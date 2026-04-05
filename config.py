# -*- coding: utf-8 -*-
"""
Конфигурация Flask приложения
Поддержка SQLite (локальная разработка) и MySQL 8.0 (продакшен на Beget)
"""
import os


class Config:
    """Базовая конфигурация для всех окружений"""
    # Секретный ключ из переменных окружения
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-prod')
    
    # Отключаем отслеживание модификаций для оптимизации
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Максимальный размер загружаемого файла (16 MB)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    
    # Распространение исключений для отладки
    PROPAGATE_EXCEPTIONS = True
    
    # Преднастройки движка SQLAlchemy для совместимости с SQLite и MySQL
    SQLALCHEMY_ENGINE_OPTIONS = {}


class DevelopmentConfig(Config):
    """Конфигурация для локальной разработки (SQLite)"""
    # SQLite по умолчанию, если DATABASE_URL не задан
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL', 
        'sqlite:///bot.db'
    )
    
    # Режим отладки включён
    DEBUG = True
    
    # Режим окружения
    FLASK_ENV = 'development'


class ProductionConfig(Config):
    """Конфигурация для продакшена (MySQL 8.0 на Beget)"""
    # URL базы данных из переменных окружения (обязательно для продакшена)
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    
    # Настройки пула соединений для MySQL 8.0
    # pool_recycle=280 — пересоздавать соединение каждые 280 секунд (меньше чем timeout на Beget)
    # pool_pre_ping=True — проверять соединение перед использованием
    # charset=utf8mb4 — поддержка emoji и всех Unicode символов
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 280,
        'pool_pre_ping': True,
        'connect_args': {
            'charset': 'utf8mb4'
        }
    }
    
    # Режим отладки выключен
    DEBUG = False
    
    # Режим окружения
    FLASK_ENV = 'production'
    
    # Пароль администратора для доступа к админ-панели
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', '')


# Словарь конфигураций для выбора по FLASK_ENV
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
