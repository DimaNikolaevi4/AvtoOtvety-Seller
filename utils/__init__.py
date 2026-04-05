# -*- coding: utf-8 -*-
"""
Вспомогательные утилиты для проекта marketplace-ai-bot
"""
import html
from typing import Optional


def sanitize_input(text: str, max_length: int = 2000) -> Optional[str]:
    """
    Санитизирует пользовательский ввод для защиты от XSS-атак.
    
    :param text: Исходная строка
    :param max_length: Максимальная длина строки (по умолчанию 2000)
    :return: Очищенная строка или None, если ввод невалиден
    """
    if not text or not isinstance(text, str):
        return None
    
    # Обрезаем пробелы в начале и конце
    cleaned = text.strip()
    
    # Проверяем, что текст не пустой после обрезки
    if not cleaned:
        return None
    
    # Ограничиваем длину
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length]
    
    # Экранируем HTML-теги (<, >, &, ", ')
    # html.escape заменяет: 
    # < → &lt;, > → &gt;, & → &amp;, " → &quot;, ' → &#x27;
    cleaned = html.escape(cleaned, quote=True)
    
    return cleaned