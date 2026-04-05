// static/js/cursor.js

(function() {
    'use strict';
    
    // Не запускать на мобильных
    if (window.matchMedia('(pointer: coarse)').matches) {
        return;
    }
    
    // Создаём SVG-курсор
    const cursor = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    cursor.id = 'customCursor';
    cursor.classList.add('custom-cursor');
    cursor.setAttribute('width', '32');
    cursor.setAttribute('height', '32');
    cursor.setAttribute('viewBox', '0 0 32 32');
    
    cursor.innerHTML = `
        <circle cx="16" cy="16" r="11" fill="none" stroke="var(--cursor-main, #667eea)" stroke-width="2" 
                style="animation: pulse-ring-rotate 2s ease-out infinite; transform-origin: 16px 16px;"/>
        <circle cx="16" cy="5" r="2.5" fill="var(--cursor-accent, #ff6600)" 
                style="animation: pulse-dot 1.5s ease-in-out infinite; animation-delay: 0s;"/>
        <circle cx="27" cy="16" r="2.5" fill="var(--cursor-accent, #ff6600)" 
                style="animation: pulse-dot 1.5s ease-in-out infinite; animation-delay: 0.3s;"/>
        <circle cx="16" cy="27" r="2.5" fill="var(--cursor-accent, #ff6600)" 
                style="animation: pulse-dot 1.5s ease-in-out infinite; animation-delay: 0.6s;"/>
        <circle cx="5" cy="16" r="2.5" fill="var(--cursor-accent, #ff6600)" 
                style="animation: pulse-dot 1.5s ease-in-out infinite; animation-delay: 0.9s;"/>
        <circle cx="16" cy="16" r="3" fill="var(--cursor-main, #667eea)" 
                style="animation: pulse-center 1.5s ease-in-out infinite;"/>
    `;
    
    document.body.appendChild(cursor);
    document.body.style.cursor = 'none';
    
    // Плавное движение
    let cursorX = 0, cursorY = 0;
    let mouseX = 0, mouseY = 0;
    
    document.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
    });
    
    function animateCursor() {
        cursorX += (mouseX - cursorX) / 10;
        cursorY += (mouseY - cursorY) / 10;
        cursor.style.left = (cursorX - 16) + 'px';
        cursor.style.top = (cursorY - 16) + 'px';
        requestAnimationFrame(animateCursor);
    }
    animateCursor();
    
    // Наведение на интерактивные элементы
    const interactive = document.querySelectorAll('a, button, .nav-link, .button, input, textarea, [role="button"]');
    interactive.forEach(el => {
        el.addEventListener('mouseenter', () => cursor.classList.add('hover'));
        el.addEventListener('mouseleave', () => cursor.classList.remove('hover'));
    });
    
    // Эффект клика
    document.addEventListener('mousedown', () => cursor.style.transform = 'scale(0.85)');
    document.addEventListener('mouseup', () => cursor.style.transform = 'scale(1)');
    
    // Экспорт функции для смены цветов
    window.updateCursorColors = function(mainColor, accentColor) {
        document.documentElement.style.setProperty('--cursor-main', mainColor);
        document.documentElement.style.setProperty('--cursor-accent', accentColor);
    };
    
    // ========== ФУНКЦИЯ СМЕНЫ ЦВЕТОВ ПО ВРЕМЕНИ ==========
    function updateColorsByTime() {
        const hour = new Date().getHours();
        let main, accent;
        
        if (hour >= 5 && hour < 12) {
            main = '#4ade80';    // утро: зелёный
            accent = '#fbbf24';  // янтарный
        } else if (hour >= 12 && hour < 18) {
            main = '#667eea';    // день: синий
            accent = '#ff6600';  // оранжевый
        } else if (hour >= 18 && hour < 22) {
            main = '#f472b6';    // вечер: розовый
            accent = '#8b5cf6';  // фиолетовый
        } else {
            main = '#818cf8';    // ночь: индиго
            accent = '#22d3ee';  // циан
        }
        
        if (typeof window.updateCursorColors === 'function') {
            window.updateCursorColors(main, accent);
        }
    }
    
    // Запускаем сразу и каждые 30 минут
    updateColorsByTime();
    setInterval(updateColorsByTime, 30 * 60 * 1000);
    
    // ========== ПЕРЕКЛЮЧАТЕЛЬ АНИМАЦИИ ==========

// Проверка сохранённой настройки
const cursorDisabled = localStorage.getItem('cursor_animation_disabled') === 'true';

// Применяем настройку при загрузке
if (cursorDisabled) {
    disableCursorAnimation();
}

// Функция отключения курсора
function disableCursorAnimation() {
    if (cursor) {
        cursor.style.display = 'none';
    }
    document.body.style.cursor = 'auto';
    document.documentElement.style.setProperty('--cursor-disabled', 'true');
}

// Функция включения курсора
function enableCursorAnimation() {
    if (cursor) {
        cursor.style.display = 'block';
    }
    document.body.style.cursor = 'none';
    document.documentElement.style.setProperty('--cursor-disabled', 'false');
}

// Переключатель
window.toggleCursorAnimation = function() {
    const isDisabled = localStorage.getItem('cursor_animation_disabled') === 'true';
    
    if (isDisabled) {
        localStorage.setItem('cursor_animation_disabled', 'false');
        enableCursorAnimation();
        showNotification('Анимация курсора включена ✨');
    } else {
        localStorage.setItem('cursor_animation_disabled', 'true');
        disableCursorAnimation();
        showNotification('Анимация курсора отключена');
    }
};

// Хоткей: Ctrl + Shift + C
document.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.shiftKey && e.code === 'KeyC') {
        e.preventDefault();
        window.toggleCursorAnimation();
    }
});

// Уведомление о переключении
function showNotification(message) {
    const notification = document.createElement('div');
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: rgba(0, 0, 0, 0.8);
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        z-index: 10000;
        animation: fadeInOut 2s ease-out;
        font-size: 14px;
    `;
    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 2000);
}

// Анимация уведомления
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeInOut {
        0% { opacity: 0; transform: translateY(10px); }
        10% { opacity: 1; transform: translateY(0); }
        90% { opacity: 1; transform: translateY(0); }
        100% { opacity: 0; transform: translateY(-10px); }
    }
`;
document.head.appendChild(style);
})();