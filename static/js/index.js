/**
 * Скрипты для главной страницы (index.html)
 */

// Обработка формы подписки на email
function initEmailForm() {
    const form = document.getElementById('emailForm');
    const messageDiv = document.getElementById('formMessage');
    
    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(form);
            try {
                const response = await fetch(form.action, {
                    method: 'POST',
                    body: formData,
                    headers: { 'Accept': 'application/json' }
                });
                const data = await response.json();
                if (response.ok && data.success) {
                    messageDiv.textContent = data.message || '✅ Спасибо! Вы в списке бета-тестеров.';
                    messageDiv.classList.add('form__message--success');
                    messageDiv.classList.remove('form__message--error');
                    form.reset();
                } else {
                    throw new Error(data.error || 'Ошибка отправки');
                }
            } catch (error) {
                messageDiv.textContent = '❌ Произошла ошибка. Попробуйте позже или напишите нам: support@автоответыселлер.рф';
                messageDiv.classList.add('form__message--error');
                messageDiv.classList.remove('form__message--success');
            }
        });
    }
}

// Анимация чисел
function animateNumber(element, start, end, duration = 2000) {
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        const current = Math.floor(progress * (end - start) + start);
        element.textContent = current;
        if (progress < 1) {
            requestAnimationFrame(step);
        }
    };
    requestAnimationFrame(step);
}

// Инициализация анимации статистики
function initStatsAnimation() {
    const statValues = document.querySelectorAll('.stat-number__value');
    if (statValues.length === 0) return;

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const el = entry.target;
                const start = parseInt(el.dataset.start) || 0;
                const end = parseInt(el.dataset.end) || 0;
                const duration = (parseFloat(el.dataset.duration) || 2) * 1000;
                if (start === end) {
                    el.textContent = end;
                } else {
                    animateNumber(el, start, end, duration);
                }
                observer.unobserve(el);
            }
        });
    }, { threshold: 0.3 });

    statValues.forEach(el => observer.observe(el));
}

// Аккордеон для FAQ
function initFAQ() {
    document.querySelectorAll('.faq-item__question').forEach(question => {
        question.addEventListener('click', () => {
            const parent = question.closest('.faq-item');
            parent.classList.toggle('active');
        });
    });
}

// Инициализация частиц (particles.js)
function initParticles() {
    if (typeof particlesJS !== 'undefined') {
        particlesJS('particles-js', {
            particles: {
                number: { value: 40 },
                color: { value: '#667eea' },
                opacity: { value: 0.3, random: true },
                size: { value: 3, random: true },
                line_linked: { enable: true, distance: 150, color: '#667eea', opacity: 0.2, width: 1 },
                move: { enable: true, speed: 1 }
            },
            interactivity: {
                events: { onhover: { enable: true, mode: 'grab' } }
            }
        });
    }
}

// Точка входа при загрузке DOM
document.addEventListener('DOMContentLoaded', function() {
    initEmailForm();
    initStatsAnimation();
    initFAQ();
    initParticles();
});
