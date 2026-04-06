# -*- coding: utf-8 -*-
"""
marketplace-ai-bot — Flask приложение для автоматизации ответов на отзывы
Домен: https://1.автоответыселлер.рф
Хостинг: Beget (Passenger + Apache)
"""
import os
import sys
import logging
import hashlib
from datetime import datetime, timedelta
from urllib.parse import urlparse
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, current_app, session
from flask_migrate import Migrate
from dotenv import load_dotenv
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf import CSRFProtect
from flask_wtf.csrf import generate_csrf
from werkzeug.utils import secure_filename
from utils.wb_api import get_wb_feedbacks
from utils.ozon_api import OzonAPI
from utils.yandex_api import YandexAPI
from utils import sanitize_input
from models import db, User, LoginHistory, ApiKey, Comment, Subscriber, ReplyHistory, Suggestion
from config import config_by_name, ProductionConfig


def get_review_rating(review, marketplace):
    """
    Извлекает рейтинг из отзыва для указанного маркетплейса.
    Возвращает целое число от 1 до 5 или 0, если рейтинг не определён.
    """
    if marketplace == 'wb':
        rating = review.get('productRating') or review.get('rating') or 0
    elif marketplace == 'ozon':
        rating = review.get('rating') or 0
    elif marketplace == 'yandex':
        rating = review.get('grade') or review.get('rating') or 0
    else:
        return 0

    if isinstance(rating, float):
        rating = int(rating)

    if rating and 1 <= rating <= 5:
        return rating
    return 0


# Загрузка переменных окружения из .env
load_dotenv()

# ==================== ИНИЦИАЛИЗАЦИЯ FLASK ====================
app = Flask(__name__)

# Выбор конфигурации в зависимости от FLASK_ENV (по умолчанию development)
flask_env = os.getenv('FLASK_ENV', 'development')
config_class = config_by_name.get(flask_env, config_by_name['default'])
app.config.from_object(config_class)

# Инициализация CSRF-защиты (после загрузки конфига)
csrf = CSRFProtect(app)

# Инициализация Flask-Migrate для управления миграциями БД
migrate = Migrate(app, db)

# Определение типа базы данных для логирования
db_uri = app.config['SQLALCHEMY_DATABASE_URI']
if db_uri.startswith('sqlite'):
    db_type = "SQLite"
elif db_uri.startswith('mysql'):
    db_type = "MySQL 8.0 (Beget)"
else:
    db_type = "Unknown"

config_name = config_class.__name__.replace('Config', '')
if not config_name:
    config_name = 'Development'

print(f"✅ Подключено к {db_type}")
print(f"🔧 Конфигурация: {config_name}")
app.logger.info(f"✅ Подключено к {db_type}")
app.logger.info(f"🔧 Конфигурация: {config_name}")

# Добавляем функцию csrf_token() в контекст шаблонов для использования в формах
@app.context_processor
def inject_csrf_token():
    return dict(csrf_token=lambda: generate_csrf())

# ==================== МОДЕЛЬ ДЛЯ ЛОГИРОВАНИЯ ЗАПРОСОВ (RATE LIMITING) ====================
class RequestLog(db.Model):
    """Таблица для логирования запросов для rate limiting (анонимов и авторизованных)"""
    __tablename__ = 'request_logs'
    id = db.Column(db.Integer, primary_key=True)
    identifier = db.Column(db.String(128), nullable=False, index=True)  # user:123 или anon:md5hash
    endpoint = db.Column(db.String(64), nullable=False)                # 'suggestion', 'send_email'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<RequestLog {self.identifier} {self.endpoint} {self.created_at}>'

# ==================== НАСТРОЙКА ЛОГИРОВАНИЯ ====================
if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')

    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s')
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info("🚀 Приложение запущено в продакшен-режиме")
    app.logger.info("📝 Логи записываются в logs/app.log")

# ==================== ЗАГРУЗКА ФАЙЛОВ ====================
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'avatars')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
try:
    os.chmod(UPLOAD_FOLDER, 0o775)
except PermissionError:
    app.logger.warning(f"⚠️ Не удалось изменить права на {UPLOAD_FOLDER}")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ==================== БД И FLASK-LOGIN ====================
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Пожалуйста, войдите для доступа к этой странице.'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================
def record_login(user, ip, user_agent):
    try:
        login_record = LoginHistory(user_id=user.id, ip_address=ip, user_agent=user_agent)
        db.session.add(login_record)
        db.session.commit()
    except Exception as e:
        app.logger.error(f"Ошибка при записи истории входа: {e}")
        db.session.rollback()

# ==================== СОЗДАНИЕ ТАБЛИЦ БД ====================
with app.app_context():
    try:
        db.create_all()
        app.logger.info("✅ Таблицы БД инициализированы")
    except Exception as e:
        app.logger.error(f"❌ Ошибка инициализации БД: {e}")

# ==================== ОБРАБОТЧИКИ ОШИБОК ====================
@app.errorhandler(404)
def not_found_error(error):
    app.logger.warning(f"404 Error: {request.url} from IP: {request.remote_addr}")
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    app.logger.error(f"500 Error: {error} from IP: {request.remote_addr}")
    return render_template('errors/500.html'), 500

# ==================== ПУБЛИЧНЫЕ МАРШРУТЫ ====================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ping')
def ping():
    return "pong", 200

@app.route('/progress')
def progress():
    return render_template('progress.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/offer')
def offer():
    return render_template('offer.html')

@app.route('/knowledge-base')
def knowledge_base():
    return render_template('knowledge_base.html')

@app.route('/beta-info')
def beta_info():
    return render_template('beta-info.html')

# ==================== БЛОГ ====================
@app.route('/blog/kak-otvechat-na-negtivnye-otzyvy-wildberries')
def article_negative_reviews():
    slug = 'kak-otvechat-na-negtivnye-otzyvy-wildberries'
    comments = Comment.query.filter_by(article_slug=slug).order_by(Comment.created_at.desc()).all()
    return render_template('blog/kak-otvechat-na-negtivnye-otzyvy-wildberries.html', comments=comments, slug=slug)

@app.route('/blog/shablony-otvetov-na-otzyvy-wildberries-ozon')
def article_templates():
    slug = 'shablony-otvetov-na-otzyvy-wildberries-ozon'
    comments = Comment.query.filter_by(article_slug=slug).order_by(Comment.created_at.desc()).all()
    return render_template('blog/shablony-otvetov-na-otzyvy-wildberries-ozon.html', comments=comments, slug=slug)

@app.route('/blog/kak-avtomatizirovat-otvety-na-otzyvy-neyroset')
def article_auto():
    slug = 'kak-avtomatizirovat-otvety-na-otzyvy-neyroset'
    comments = Comment.query.filter_by(article_slug=slug).order_by(Comment.created_at.desc()).all()
    return render_template('blog/kak-avtomatizirovat-otvety-na-otzyvy-neyroset.html', comments=comments, slug=slug)

@app.route('/blog/<slug>/comment', methods=['POST'])
def add_comment(slug):
    name = request.form.get('name', '').strip()
    text = request.form.get('text', '').strip()
    honeypot = request.form.get('_honeypot', '')

    if honeypot:
        return redirect(request.referrer or url_for('index'))

    if not name or not text:
        flash('Пожалуйста, заполните имя и комментарий.', 'error')
        return redirect(request.referrer or url_for('index'))

    try:
        comment = Comment(article_slug=slug, author_name=name, text=text)
        db.session.add(comment)
        db.session.commit()
        app.logger.info(f"💬 Комментарий добавлен к статье {slug}")
        flash('Спасибо! Комментарий добавлен.', 'success')
    except Exception as e:
        app.logger.error(f"Ошибка при добавлении комментария: {e}")
        flash('Произошла ошибка. Попробуйте позже.', 'error')
        db.session.rollback()

    return redirect(request.referrer or url_for('index'))

# ==================== АВТОРИЗАЦИЯ ====================
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')

        if not email or not password or not confirm:
            flash('Все поля обязательны', 'danger')
            return redirect(url_for('register'))

        if len(password) < 6:
            flash('Пароль должен содержать минимум 6 символов', 'danger')
            return redirect(url_for('register'))

        if password != confirm:
            flash('Пароли не совпадают', 'danger')
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            flash('Пользователь с таким email уже существует', 'danger')
            return redirect(url_for('register'))

        try:
            user = User(email=email, name=email.split('@')[0])
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            app.logger.info(f"✅ Новый пользователь зарегистрирован: {email}")
            flash('Регистрация прошла успешно! Теперь вы можете войти.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            app.logger.error(f"❌ Ошибка регистрации: {e}")
            db.session.rollback()
            flash('Произошла ошибка при регистрации', 'danger')
            return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash('Введите email и пароль', 'danger')
            return redirect(url_for('login'))

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            app.logger.info(f"✅ Вход выполнен: {email}")
            return redirect(url_for('dashboard'))
        else:
            app.logger.warning(f"⚠️ Неудачная попытка входа: {email}")
            flash('Неверный email или пароль', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# ==================== ПРОФИЛЬ ====================
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        action = request.form.get('action')

        try:
            if action == 'update_profile':
                new_name = request.form.get('name', '').strip()
                new_email = request.form.get('email', '').strip()

                if new_email and '@' in new_email:
                    existing = User.query.filter(User.email == new_email, User.id != current_user.id).first()
                    if existing:
                        flash('Этот email уже используется', 'danger')
                    else:
                        current_user.email = new_email
                        flash('Email успешно изменён', 'success')
                else:
                    flash('Некорректный email', 'danger')

                if new_name:
                    current_user.name = new_name
                    flash('Имя успешно изменено', 'success')

                db.session.commit()

            elif action == 'change_password':
                old_password = request.form.get('old_password')
                new_password = request.form.get('new_password')
                confirm = request.form.get('confirm_password')

                if not current_user.check_password(old_password):
                    flash('Неверный текущий пароль', 'danger')
                elif new_password != confirm:
                    flash('Новые пароли не совпадают', 'danger')
                elif len(new_password) < 6:
                    flash('Пароль должен быть не менее 6 символов', 'danger')
                else:
                    current_user.set_password(new_password)
                    db.session.commit()
                    flash('Пароль успешно изменён', 'success')

            elif action == 'update_notifications':
                current_user.email_notifications = 'email_notifications' in request.form
                current_user.push_notifications = 'push_notifications' in request.form
                db.session.commit()
                flash('Настройки уведомлений обновлены', 'success')

            elif action == 'update_auto_reply':
                current_user.auto_reply_enabled = 'auto_reply_enabled' in request.form
                db.session.commit()
                flash('Настройки автоответа обновлены', 'success')

            return redirect(url_for('profile'))

        except Exception as e:
            app.logger.error(f"Ошибка при обновлении профиля: {e}")
            flash('Произошла ошибка. Попробуйте позже.', 'danger')
            db.session.rollback()
            return redirect(url_for('profile'))

    login_history = LoginHistory.query.filter_by(user_id=current_user.id).limit(5).all()
    return render_template('profile.html', user=current_user, login_history=login_history)

@app.route('/upload-avatar', methods=['POST'])
@login_required
def upload_avatar():
    if 'avatar' not in request.files:
        flash('Файл не выбран', 'danger')
        return redirect(url_for('profile'))

    file = request.files['avatar']
    if file.filename == '':
        flash('Файл не выбран', 'danger')
        return redirect(url_for('profile'))

    try:
        if file and allowed_file(file.filename):
            filename = secure_filename(f"{current_user.id}_{file.filename}")
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            if current_user.avatar:
                old_path = os.path.join(app.config['UPLOAD_FOLDER'], current_user.avatar)
                if os.path.exists(old_path):
                    os.remove(old_path)

            current_user.avatar = filename
            db.session.commit()
            app.logger.info(f"🖼️ Аватар загружен для пользователя {current_user.id}")
            flash('Аватар успешно загружен', 'success')
        else:
            flash('Недопустимый формат файла. Разрешены: png, jpg, jpeg, gif', 'danger')
    except Exception as e:
        app.logger.error(f"Ошибка загрузки аватара: {e}")
        flash('Ошибка при загрузке файла', 'danger')
        db.session.rollback()

    return redirect(url_for('profile'))

@app.route('/delete-account', methods=['POST'])
@login_required
def delete_account():
    try:
        email = current_user.email
        ApiKey.query.filter_by(user_id=current_user.id).delete()
        ReplyHistory.query.filter_by(user_id=current_user.id).delete()
        LoginHistory.query.filter_by(user_id=current_user.id).delete()

        if current_user.avatar:
            avatar_path = os.path.join(app.config['UPLOAD_FOLDER'], current_user.avatar)
            if os.path.exists(avatar_path):
                os.remove(avatar_path)

        db.session.delete(current_user)
        db.session.commit()
        app.logger.info(f"🗑️ Аккаунт удалён: {email}")

        logout_user()
        flash('Ваш аккаунт успешно удалён', 'success')
    except Exception as e:
        app.logger.error(f"Ошибка при удалении аккаунта: {e}")
        flash('Произошла ошибка при удалении', 'danger')
        db.session.rollback()

    return redirect(url_for('index'))

# ==================== ДАШБОРД ====================
@app.route('/dashboard')
@login_required
def dashboard():
    api_keys = current_user.api_keys
    feedbacks_by_marketplace = {'wildberries': [], 'ozon': [], 'yandex': []}

    has_wb = any(key.marketplace == 'wb' for key in api_keys)
    has_ozon = any(key.marketplace == 'ozon' for key in api_keys)
    has_yandex = any(key.marketplace == 'yandex' for key in api_keys)

    total_reviews = 0
    positive = 0
    neutral = 0
    negative = 0
    total_rating_sum = 0

    for key in api_keys:
        try:
            if key.marketplace == 'wb':
                feedbacks = get_wb_feedbacks(key.api_key)
                if feedbacks:
                    feedbacks_by_marketplace['wildberries'].extend(feedbacks)
                    for fb in feedbacks:
                        rating = get_review_rating(fb, 'wb')
                        if rating >= 4:
                            positive += 1
                        elif rating == 3:
                            neutral += 1
                        elif 1 <= rating <= 2:
                            negative += 1
                        else:
                            neutral += 1
                        if rating:
                            total_rating_sum += rating
                    total_reviews += len(feedbacks)

            elif key.marketplace == 'ozon' and key.ozon_client_id and key.ozon_api_key:
                ozon = OzonAPI(key.ozon_client_id, key.ozon_api_key)
                ozon_feedbacks = ozon.get_feedbacks(limit=50)
                feedbacks_by_marketplace['ozon'].extend(ozon_feedbacks)
                for fb in ozon_feedbacks:
                    rating = get_review_rating(fb, 'ozon')
                    if rating >= 4:
                        positive += 1
                    elif rating == 3:
                        neutral += 1
                    elif 1 <= rating <= 2:
                        negative += 1
                    else:
                        neutral += 1
                    if rating:
                        total_rating_sum += rating
                total_reviews += len(ozon_feedbacks)

            elif key.marketplace == 'yandex' and key.api_key:
                yandex = YandexAPI(key.api_key)
                yandex_feedbacks = yandex.get_feedbacks(limit=50)
                feedbacks_by_marketplace['yandex'].extend(yandex_feedbacks)
                for fb in yandex_feedbacks:
                    rating = get_review_rating(fb, 'yandex')
                    if rating >= 4:
                        positive += 1
                    elif rating == 3:
                        neutral += 1
                    elif 1 <= rating <= 2:
                        negative += 1
                    else:
                        neutral += 1
                    if rating:
                        total_rating_sum += rating
                total_reviews += len(yandex_feedbacks)

        except Exception as e:
            app.logger.error(f"Ошибка получения отзывов ({key.marketplace}): {e}")
            flash(f'Ошибка при получении отзывов {key.marketplace}', 'danger')

    if total_reviews > 0:
        avg_rating = round(total_rating_sum / total_reviews, 1)
        stats = {
            'total_reviews': total_reviews,
            'avg_rating': avg_rating,
            'requests_today': 28,
            'active_platforms': sum([has_wb, has_ozon, has_yandex])
        }
    else:
        stats = {'total_reviews': 0, 'avg_rating': 0, 'requests_today': 0, 'active_platforms': 0}
        positive = neutral = negative = 0

    review_summary = {'positive': positive, 'neutral': neutral, 'negative': negative}
    chart_data = {'labels': [], 'values': []}
    reply_history = ReplyHistory.query.filter_by(user_id=current_user.id).limit(5).all()

    return render_template('dashboard.html',
                           api_keys=api_keys,
                           feedbacks=feedbacks_by_marketplace,
                           has_wb=has_wb, has_ozon=has_ozon, has_yandex=has_yandex,
                           stats=stats, review_summary=review_summary,
                           chart_data=chart_data, history=reply_history,
                           auto_reply_enabled=current_user.auto_reply_enabled)

# ==================== ИСТОРИЯ ОТВЕТОВ ====================
@app.route('/history')
@login_required
def history():
    reply_history = ReplyHistory.query.filter_by(user_id=current_user.id).order_by(ReplyHistory.created_at.desc()).all()
    return render_template('history.html', history=reply_history)

# ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ БЕЗОПАСНОСТИ ====================

def get_user_identifier():
    """
    Возвращает идентификатор пользователя для проверки лимитов.
    Если авторизован -> user:ID.
    Если аноним -> anon:md5(IP + User-Agent).
    """
    if current_user.is_authenticated:
        return f"user:{current_user.id}"

    ip = request.remote_addr or '127.0.0.1'
    ua = request.headers.get('User-Agent', 'unknown')
    raw_id = f"{ip}:{ua}"
    hashed_id = hashlib.md5(raw_id.encode('utf-8')).hexdigest()
    return f"anon:{hashed_id}"

def check_rate_limit(limit_count=3, window_hours=1, endpoint='suggestion'):
    """
    Проверяет лимит запросов для текущего пользователя (авторизованного или анонима).
    Возвращает (True, None) если лимит не превышен, или (False, error_message) если превышен.
    Логирует запрос в таблицу RequestLog.
    """
    identifier = get_user_identifier()
    cutoff = datetime.utcnow() - timedelta(hours=window_hours)

    # Считаем количество запросов от этого идентификатора для данного эндпоинта за период
    count = RequestLog.query.filter(
        RequestLog.identifier == identifier,
        RequestLog.endpoint == endpoint,
        RequestLog.created_at >= cutoff
    ).count()

    if count >= limit_count:
        app.logger.warning(f"Rate limit hit: {identifier} on {endpoint}, count={count}, limit={limit_count}")
        return False, f"Превышен лимит запросов. Пожалуйста, подождите {window_hours} час(а)."

    # Логируем текущий запрос
    try:
        log = RequestLog(identifier=identifier, endpoint=endpoint)
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        app.logger.error(f"Failed to log request for rate limiting: {e}")
        db.session.rollback()
        # Даже если лог не сохранился, не блокируем запрос
    return True, None

def check_referer():
    """
    Ослабленная проверка Referer для совместимости с хостингом BeGet.
    Возвращает True, если Referer отсутствует или совпадает с доменом.
    """
    referrer = request.headers.get('Referer', '')
    if not referrer:
        return True

    parsed_ref = urlparse(referrer).netloc.lower()
    host = urlparse(request.url).netloc.lower()

    if parsed_ref == host:
        return True

    ref_parts = parsed_ref.replace('www.', '').split('.')
    host_parts = host.replace('www.', '').split('.')

    if len(ref_parts) >= 2 and len(host_parts) >= 2:
        ref_domain = '.'.join(ref_parts[-2:])
        host_domain = '.'.join(host_parts[-2:])
        if ref_domain == host_domain:
            return True

    app.logger.warning(
        f"CSRF warning: Referer={referrer}, Host={host}, IP={request.remote_addr}. "
        f"Запрос разрешён в режиме бета-тестирования."
    )
    return True

# ==================== API ЭНДПОИНТЫ ====================
@app.route('/api/chart-data')
@csrf.exempt
@login_required
def chart_data_api():
    period = request.args.get('period', default='7', type=int)
    return jsonify({'labels': [], 'values': []})

@app.route('/api/generate-reply', methods=['POST'])
@csrf.exempt
@login_required
def generate_reply():
    data = request.get_json() or {}
    marketplace = data.get('marketplace', '')
    reply = f"Спасибо за отзыв! Мы ценим ваше мнение. (Заглушка для {marketplace})"
    return jsonify({'reply': reply})

@app.route('/api/save-reply', methods=['POST'])
@csrf.exempt
@login_required
def save_reply():
    data = request.get_json() or {}
    marketplace = data.get('marketplace')
    review_text = data.get('review_text')
    reply_text = data.get('reply_text')

    if not all([marketplace, review_text, reply_text]):
        return jsonify({'error': 'Недостаточно данных'}), 400

    try:
        reply_entry = ReplyHistory(
            user_id=current_user.id,
            marketplace=marketplace,
            review_text=review_text,
            reply_text=reply_text
        )
        db.session.add(reply_entry)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        app.logger.error(f"Ошибка сохранения ответа: {e}")
        return jsonify({'error': 'Ошибка сервера'}), 500

@app.route('/api/auto-reply-settings', methods=['POST'])
@csrf.exempt
@login_required
def update_auto_reply_settings():
    data = request.get_json() or {}
    current_user.auto_reply_enabled = data.get('enabled', False)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/notification-settings', methods=['POST'])
@csrf.exempt
@login_required
def update_notification_settings():
    data = request.get_json() or {}
    current_user.email_notifications = data.get('email', False)
    current_user.push_notifications = data.get('push', False)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/add-api-key', methods=['POST'])
@login_required
def add_api_key():
    marketplace = request.form.get('marketplace')
    api_key = request.form.get('api_key')

    if not marketplace or not api_key:
        flash('Заполните все поля', 'error')
        return redirect(url_for('dashboard'))

    if marketplace == 'ozon':
        flash('Для Ozon используйте отдельную форму добавления ключей', 'warning')
        return redirect(url_for('dashboard'))

    try:
        new_key = ApiKey(user_id=current_user.id, marketplace=marketplace, api_key=api_key)
        db.session.add(new_key)
        db.session.commit()
        app.logger.info(f"🔑 API-ключ добавлен: {marketplace} для пользователя {current_user.id}")
        flash('API-ключ успешно добавлен', 'success')
    except Exception as e:
        app.logger.error(f"Ошибка добавления ключа: {e}")
        flash('Ошибка при сохранении ключа', 'error')
        db.session.rollback()

    return redirect(url_for('dashboard'))

@app.route('/add-ozon-keys', methods=['POST'])
@login_required
def add_ozon_keys():
    client_id = request.form.get('ozon_client_id')
    api_key = request.form.get('ozon_api_key')

    if not client_id or not api_key:
        flash('Заполните оба поля для Ozon', 'error')
        return redirect(url_for('dashboard'))

    try:
        existing = ApiKey.query.filter_by(user_id=current_user.id, marketplace='ozon').first()
        if existing:
            existing.ozon_client_id = client_id
            existing.ozon_api_key = api_key
        else:
            new_key = ApiKey(user_id=current_user.id, marketplace='ozon',
                           api_key='', ozon_client_id=client_id, ozon_api_key=api_key)
            db.session.add(new_key)
        db.session.commit()
        app.logger.info(f"🔑 Ключи Ozon добавлены для пользователя {current_user.id}")
        flash('Ключи Ozon успешно добавлены', 'success')
    except Exception as e:
        app.logger.error(f"Ошибка добавления ключей Ozon: {e}")
        flash('Ошибка при сохранении ключей', 'error')
        db.session.rollback()

    return redirect(url_for('dashboard'))

@app.route('/delete-api-key/<int:key_id>', methods=['POST'])
@login_required
def delete_api_key(key_id):
    key = ApiKey.query.get_or_404(key_id)
    if key.user_id != current_user.id:
        flash('У вас нет прав на удаление этого ключа', 'error')
        return redirect(url_for('dashboard'))

    try:
        db.session.delete(key)
        db.session.commit()
        app.logger.info(f"🗑️ API-ключ #{key_id} удалён")
        flash('API-ключ удалён', 'success')
    except Exception as e:
        app.logger.error(f"Ошибка удаления ключа: {e}")
        flash('Ошибка при удалении', 'error')
        db.session.rollback()

    return redirect(url_for('dashboard'))

# ==================== OZON API ЭНДПОИНТЫ ====================
@app.route('/api/ozon/feedbacks')
@csrf.exempt
@login_required
def get_ozon_feedbacks_api():
    api_key_obj = ApiKey.query.filter_by(user_id=current_user.id, marketplace='ozon').first()
    if not api_key_obj or not api_key_obj.ozon_client_id or not api_key_obj.ozon_api_key:
        return jsonify({'error': 'Ozon API keys not configured'}), 400
    try:
        ozon = OzonAPI(api_key_obj.ozon_client_id, api_key_obj.ozon_api_key)
        return jsonify(ozon.get_feedbacks(limit=50))
    except Exception as e:
        app.logger.error(f"Ozon API error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ozon/answer', methods=['POST'])
@csrf.exempt
@login_required
def answer_ozon_feedback():
    data = request.json or {}
    feedback_id = data.get('feedback_id')
    text = data.get('text')
    api_key_obj = ApiKey.query.filter_by(user_id=current_user.id, marketplace='ozon').first()
    if not api_key_obj or not api_key_obj.ozon_client_id or not api_key_obj.ozon_api_key:
        return jsonify({'error': 'Ozon API keys not configured'}), 400
    try:
        ozon = OzonAPI(api_key_obj.ozon_client_id, api_key_obj.ozon_api_key)
        return jsonify(ozon.answer_feedback(feedback_id, text))
    except Exception as e:
        app.logger.error(f"Ozon answer error: {e}")
        return jsonify({'error': str(e)}), 500

# ==================== YANDEX API ЭНДПОИНТЫ ====================
@app.route('/api/yandex/feedbacks')
@csrf.exempt
@login_required
def get_yandex_feedbacks_api():
    api_key_obj = ApiKey.query.filter_by(user_id=current_user.id, marketplace='yandex').first()
    if not api_key_obj or not api_key_obj.api_key:
        return jsonify({'error': 'Yandex API key not configured'}), 400
    try:
        yandex = YandexAPI(api_key_obj.api_key)
        return jsonify(yandex.get_feedbacks(limit=50))
    except Exception as e:
        app.logger.error(f"Yandex API error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/yandex/answer', methods=['POST'])
@csrf.exempt
@login_required
def answer_yandex_feedback():
    data = request.json or {}
    feedback_id = data.get('feedback_id')
    text = data.get('text')
    api_key_obj = ApiKey.query.filter_by(user_id=current_user.id, marketplace='yandex').first()
    if not api_key_obj or not api_key_obj.api_key:
        return jsonify({'error': 'Yandex API key not configured'}), 400
    try:
        yandex = YandexAPI(api_key_obj.api_key)
        return jsonify(yandex.answer_feedback(feedback_id, text))
    except Exception as e:
        app.logger.error(f"Yandex answer error: {e}")
        return jsonify({'error': str(e)}), 500

# ==================== ПРЕДЛОЖЕНИЯ И ПОДПИСКА ====================
@app.route('/api/suggestion', methods=['POST'])
@csrf.exempt
@login_required
def add_suggestion():
    """
    Обработка предложения от пользователя с rate limiting (3 в час).
    """
    # Проверка лимита для эндпоинта 'suggestion'
    allowed, error_msg = check_rate_limit(limit_count=3, window_hours=1, endpoint='suggestion')
    if not allowed:
        return jsonify({'error': error_msg}), 429

    if not check_referer():
        return jsonify({'error': 'Запрос отклонён по соображениям безопасности. Попробуйте обновить страницу.'}), 403

    data = request.get_json() or {}
    raw_text = data.get('text', '')

    clean_text = sanitize_input(raw_text)
    if not clean_text:
        app.logger.info(f"Invalid input from user_id={current_user.id}: {raw_text[:50]}...")
        return jsonify({'error': 'Пожалуйста, введите корректный текст предложения (без HTML-тегов, 1-2000 символов).'}), 400

    try:
        suggestion = Suggestion(user_id=current_user.id, text=clean_text, status='new')
        db.session.add(suggestion)
        db.session.commit()
        app.logger.info(f"💬 Предложение сохранено: ID={suggestion.id}, User={current_user.id}")
        return jsonify({'success': True})
    except Exception as e:
        app.logger.error(f"Ошибка сохранения предложения: {e}")
        db.session.rollback()
        return jsonify({'error': 'Ошибка сервера'}), 500

@app.route('/send-email', methods=['POST'])
@csrf.exempt
def send_email():
    """
    Подписка на новости с rate limiting (5 в час для одного идентификатора).
    """
    # Проверка лимита для эндпоинта 'send_email'
    allowed, error_msg = check_rate_limit(limit_count=5, window_hours=1, endpoint='send_email')
    if not allowed:
        return jsonify({'success': False, 'error': error_msg}), 429

    email = request.form.get('email')
    if not email or '@' not in email:
        return jsonify({'success': False, 'error': 'Некорректный email'}), 400
    try:
        existing = Subscriber.query.filter_by(email=email).first()
        if existing:
            return jsonify({'success': True, 'message': '✅ Вы уже подписаны! Спасибо.'}), 200
        subscriber = Subscriber(email=email)
        db.session.add(subscriber)
        db.session.commit()
        return jsonify({'success': True, 'message': '✅ Спасибо! Вы в списке бета-тестеров.'})
    except Exception as e:
        app.logger.error(f"Ошибка подписки: {e}")
        return jsonify({'success': False, 'error': 'Ошибка сервера'}), 500

# ==================== ОТЛАДКА (удалить в продакшене!) ====================
@app.route('/debug')
@login_required
def debug():
    import traceback
    try:
        api_keys = current_user.api_keys
        return f"User: {current_user.email}, API keys: {len(api_keys)}"
    except Exception as e:
        return f"<pre>{traceback.format_exc()}</pre>", 500

# ==================== ЗАПУСК ====================
if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)

# ==================== АДМИН-ПАНЕЛЬ ====================
def admin_required(f):
    from functools import wraps
    from flask import session

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_authenticated'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    from flask import session

    if request.method == 'POST':
        if not check_referer():
            flash('Запрос отклонён по соображениям безопасности. Попробуйте обновить страницу.', 'danger')
            return redirect(url_for('admin_login'))

        password = request.form.get('password', '')
        admin_password = app.config.get('ADMIN_PASSWORD', '') or ProductionConfig.ADMIN_PASSWORD

        if password == admin_password and admin_password:
            session['admin_authenticated'] = True
            session['admin_email'] = 'admin'
            app.logger.info(f"✅ Вход в админку выполнен: admin")
            return redirect(url_for('admin_suggestions'))
        else:
            app.logger.warning(f"⚠️ Неверный пароль админки, IP={request.remote_addr}")
            flash('Неверный пароль', 'danger')
            return redirect(url_for('admin_login'))

    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    from flask import session
    session.pop('admin_authenticated', None)
    session.pop('admin_email', None)
    app.logger.info("🚪 Выход из админки")
    return redirect(url_for('index'))

@app.route('/admin/suggestions')
@admin_required
def admin_suggestions():
    from flask import session

    page = request.args.get('page', 1, type=int)
    per_page = 50

    suggestions_pagination = Suggestion.query.order_by(Suggestion.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    app.logger.info(f"📋 Админ просмотрел предложения: страница {page}")

    return render_template('admin/suggestions.html',
                         pagination=suggestions_pagination,
                         suggestions=suggestions_pagination.items)

@app.route('/admin/suggestions/export')
@admin_required
def export_suggestions_csv():
    from flask import session, make_response
    import csv
    import io
    from datetime import datetime

    all_suggestions = Suggestion.query.order_by(Suggestion.created_at.desc()).all()

    output = io.StringIO()
    output.write('\ufeff')

    writer = csv.writer(output)
    writer.writerow(['id', 'created_at', 'user_email', 'suggestion_text', 'status'])

    for suggestion in all_suggestions:
        user_email = suggestion.user.email if suggestion.user else 'unknown'
        writer.writerow([
            suggestion.id,
            suggestion.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            user_email,
            suggestion.text,
            'new'
        ])

    filename = f"suggestions_{datetime.now().strftime('%Y%m%d')}.csv"
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    response.headers['Content-Type'] = 'text/csv; charset=utf-8'

    admin_email = session.get('admin_email', 'admin')
    app.logger.info(f"📥 CSV экспортирован пользователем {admin_email}")

    return response
