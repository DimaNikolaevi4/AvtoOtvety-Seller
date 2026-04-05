/**
 * dashboard.js — интерактив для кабинета пользователя
 * Маркетплейсы: Wildberries, Ozon, Яндекс Маркет
 */

document.addEventListener('DOMContentLoaded', function() {
    
    // ===== 1. Переключатели маркетплейсов (сохранение состояния) =====
    document.querySelectorAll('.toggle-switch input[type="checkbox"]').forEach(toggle => {
        toggle.addEventListener('change', function() {
            const marketplace = this.dataset.marketplace;
            const statusEl = document.getElementById(`${marketplace}-status`);
            
            fetch('/api/auto-reply-settings', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({enabled: this.checked, marketplace: marketplace})
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    if (statusEl) statusEl.textContent = this.checked ? 'Подключён' : 'Не подключён';
                    showFlash('Настройки обновлены', 'success');
                } else {
                    this.checked = !this.checked; // откат при ошибке
                    showFlash('Ошибка сохранения', 'danger');
                }
            })
            .catch(err => {
                console.error('Error:', err);
                this.checked = !this.checked;
                showFlash('Ошибка сети', 'danger');
            });
        });
    });

    // ===== 2. Переключатель автоответов (глобальный) =====
    const autoReplyToggle = document.getElementById('auto_reply_toggle');
    if (autoReplyToggle) {
        autoReplyToggle.addEventListener('change', function() {
            fetch('/api/auto-reply-settings', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({enabled: this.checked})
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    showFlash('Автоответы ' + (this.checked ? 'включены' : 'выключены'), 'success');
                } else {
                    this.checked = !this.checked;
                    showFlash('Ошибка сохранения', 'danger');
                }
            })
            .catch(err => {
                console.error('Error:', err);
                this.checked = !this.checked;
                showFlash('Ошибка сети', 'danger');
            });
        });
    }

    // ===== 3. Кнопки "Настроить" → открытие модального окна с нужным маркетплейсом =====
    document.querySelectorAll('[data-bs-target="#apiKeyModal"]').forEach(btn => {
        btn.addEventListener('click', function() {
            const mp = this.dataset.marketplace;
            document.getElementById('modalMarketplace').value = mp;
            
            // Показываем нужные поля
            document.getElementById('standardKeyFields').classList.toggle('d-none', mp === 'ozon');
            document.getElementById('ozonKeyFields').classList.toggle('d-none', mp !== 'ozon');
            
            // Показываем нужные ссылки помощи
            document.getElementById('wbHelpLink').classList.toggle('d-none', mp !== 'wb');
            document.getElementById('yaHelpLink').classList.toggle('d-none', mp !== 'yandex');
            
            // Обновляем заголовок
            const titles = {wb: 'Wildberries', ozon: 'Ozon', yandex: 'Яндекс Маркет'};
            document.querySelector('#apiKeyModal .modal-title').textContent = `Настройка API-ключа — ${titles[mp]}`;
        });
    });

    // ===== 4. Сохранение API-ключа =====
    document.getElementById('saveApiKeyBtn')?.addEventListener('click', function() {
        const marketplace = document.getElementById('modalMarketplace').value;
        const form = document.getElementById('apiKeyForm');
        const formData = new FormData(form);
        
        const url = marketplace === 'ozon' ? '/add-ozon-keys' : '/add-api-key';
        
        fetch(url, {
            method: 'POST',
            body: formData
        })
        .then(r => {
            if (r.redirected) {
                window.location.reload(); // перезагрузка для применения изменений
            } else {
                return r.json();
            }
        })
        .catch(err => {
            console.error('Error:', err);
            showFlash('Ошибка при сохранении ключа', 'danger');
        });
    });

    // ===== 5. Кнопки "Сгенерировать ответ" (открытие модалки) =====
    document.querySelectorAll('.generate-reply-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const marketplace = this.dataset.marketplace;
            openReplyModal(marketplace, '', '');
        });
    });

    // ===== 6. Кнопки "Ответить" у конкретных отзывов =====
    document.querySelectorAll('.reply-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const marketplace = this.dataset.marketplace;
            const feedbackId = this.dataset.feedbackId;
            const reviewText = this.dataset.reviewText;
            openReplyModal(marketplace, feedbackId, reviewText);
        });
    });

    // Функция открытия модального окна ответа
    function openReplyModal(marketplace, feedbackId, reviewText) {
        document.getElementById('replyMarketplace').value = marketplace;
        document.getElementById('replyFeedbackId').value = feedbackId || '';
        document.getElementById('modalReviewText').value = reviewText || '';
        document.getElementById('generatedAnswer').value = '';
        document.getElementById('finalAnswer').value = '';
        document.getElementById('generateStatus').textContent = '';
        
        const modal = new bootstrap.Modal(document.getElementById('replyModal'));
        modal.show();
    }

    // ===== 7. Генерация ответа (ИИ) =====
    document.getElementById('generateBtn')?.addEventListener('click', function() {
        const btn = this;
        const statusEl = document.getElementById('generateStatus');
        const marketplace = document.getElementById('replyMarketplace').value;
        const reviewText = document.getElementById('modalReviewText').value;
        
        if (!reviewText.trim()) {
            statusEl.textContent = 'Введите текст отзыва';
            statusEl.className = 'form-text text-danger';
            return;
        }
        
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Генерация...';
        statusEl.textContent = '';
        
        fetch('/api/generate-reply', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({marketplace, review_text: reviewText})
        })
        .then(r => r.json())
        .then(data => {
            if (data.reply) {
                document.getElementById('generatedAnswer').value = data.reply;
                document.getElementById('finalAnswer').value = data.reply;
                statusEl.textContent = '✅ Ответ сгенерирован';
                statusEl.className = 'form-text text-success';
            } else {
                statusEl.textContent = data.error || 'Ошибка генерации';
                statusEl.className = 'form-text text-danger';
            }
        })
        .catch(err => {
            console.error('Error:', err);
            statusEl.textContent = 'Ошибка сети';
            statusEl.className = 'form-text text-danger';
        })
        .finally(() => {
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-magic me-1"></i>Сгенерировать';
        });
    });

    // ===== 8. Сохранение ответа =====
    document.getElementById('saveReplyBtn')?.addEventListener('click', function() {
        const marketplace = document.getElementById('replyMarketplace').value;
        const feedbackId = document.getElementById('replyFeedbackId').value;
        const reviewText = document.getElementById('modalReviewText').value;
        const replyText = document.getElementById('finalAnswer').value.trim();
        
        if (!replyText) {
            showFlash('Введите текст ответа', 'warning');
            return;
        }
        
        fetch('/api/save-reply', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                marketplace,
                feedback_id: feedbackId,
                review_text: reviewText,
                reply_text: replyText
            })
        })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                showFlash('✅ Ответ сохранён!', 'success');
                bootstrap.Modal.getInstance(document.getElementById('replyModal')).hide();
                setTimeout(() => location.reload(), 1000);
            } else {
                showFlash(data.error || 'Ошибка сохранения', 'danger');
            }
        })
        .catch(err => {
            console.error('Error:', err);
            showFlash('Ошибка сети', 'danger');
        });
    });

    // ===== 9. Отправка предложений =====
    document.getElementById('suggestionForm')?.addEventListener('submit', function(e) {
        e.preventDefault();
        const text = document.getElementById('suggestionText').value.trim();
        const statusEl = document.getElementById('suggestionStatus');
        const btn = document.getElementById('sendSuggestionBtn');
        
        if (text.length < 10) {
            statusEl.innerHTML = '<span class="text-danger">Минимум 10 символов</span>';
            return;
        }
        
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Отправка...';
        
        fetch('/api/suggestion', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({text})
        })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                statusEl.innerHTML = '<span class="text-success fw-bold">✅ Спасибо! Ваше предложение отправлено.</span>';
                document.getElementById('suggestionForm').reset();
                setTimeout(() => statusEl.innerHTML = '', 5000);
            } else {
                statusEl.innerHTML = `<span class="text-danger">❌ ${data.error || 'Ошибка'}</span>`;
            }
        })
        .catch(err => {
            console.error('Error:', err);
            statusEl.innerHTML = '<span class="text-danger">❌ Ошибка сети</span>';
        })
        .finally(() => {
            btn.disabled = false;
            btn.textContent = 'Отправить предложение';
        });
    });

    // ===== 10. Вспомогательная функция для flash-сообщений =====
    function showFlash(message, category = 'info') {
        const container = document.querySelector('.container.py-4');
        const alert = document.createElement('div');
        alert.className = `alert alert-${category} alert-dismissible fade show mb-4`;
        alert.role = 'alert';
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        container.insertBefore(alert, container.firstChild);
        
        setTimeout(() => {
            if (alert.parentNode) alert.remove();
        }, 5000);
    }

    // ===== 11. Инициализация графика (заглушка) =====
    const ctx = document.getElementById('reviewsChart');
    if (ctx) {
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Отзывы',
                    data: [],
                    borderColor: '#0d6efd',
                    tension: 0.3,
                    fill: false
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {beginAtZero: true}
                }
            }
        });
    }
});
