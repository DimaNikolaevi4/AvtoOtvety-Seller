#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для генерации sitemap.xml
Используется для автоматического обновления карты сайта
"""
import os
from datetime import datetime
from urllib.parse import urljoin

# Базовый URL сайта (берется из переменных окружения или используется по умолчанию)
BASE_URL = os.getenv('SITE_URL', 'https://1.автоответыселлер.рф')

# Список всех статических маршрутов сайта
STATIC_ROUTES = [
    '/',
    '/progress',
    '/privacy',
    '/offer',
    '/knowledge-base',
    '/beta-info',
    '/login',
    '/register',
    '/blog/kak-otvechat-na-negtivnye-otzyvy-wildberries',
    '/blog/shablony-otvetov-na-otzyvy-wildberries-ozon',
    '/blog/kak-avtomatizirovat-otvety-na-otzyvy-neyroset',
]

# Приоритеты для разных типов страниц
ROUTE_PRIORITIES = {
    '/': 1.0,
    '/login': 0.3,
    '/register': 0.3,
    '/privacy': 0.5,
    '/offer': 0.5,
    '/blog/': 0.7,
}

def get_priority(route):
    """Определяет приоритет страницы на основе маршрута"""
    for prefix, priority in ROUTE_PRIORITIES.items():
        if route.startswith(prefix):
            return priority
    return 0.6  # Приоритет по умолчанию

def generate_sitemap(output_path='sitemap.xml'):
    """Генерирует файл sitemap.xml"""
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    
    for route in STATIC_ROUTES:
        url = urljoin(BASE_URL, route.lstrip('/'))
        priority = get_priority(route)
        
        xml_lines.extend([
            '  <url>',
            f'    <loc>{url}</loc>',
            f'    <lastmod>{today}</lastmod>',
            f'    <changefreq>weekly</changefreq>',
            f'    <priority>{priority}</priority>',
            '  </url>',
        ])
    
    xml_lines.append('</urlset>')
    
    # Записываем в файл
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(xml_lines))
    
    print(f"✅ Sitemap.xml успешно сгенерирован: {output_path}")
    print(f"📊 Всего URL: {len(STATIC_ROUTES)}")
    print(f"🌐 Базовый URL: {BASE_URL}")

if __name__ == '__main__':
    generate_sitemap()
