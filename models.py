from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=True)
    password_hash = db.Column(db.String(128), nullable=False)
    avatar = db.Column(db.String(200), nullable=True)
    auto_reply_enabled = db.Column(db.Boolean, default=False)
    email_notifications = db.Column(db.Boolean, default=True)
    push_notifications = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)  # Флаг администратора

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class LoginHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    login_time = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(200), nullable=True)

    user = db.relationship('User', backref=db.backref('login_history', lazy=True, order_by='LoginHistory.login_time.desc()'))

class ApiKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    marketplace = db.Column(db.String(50), nullable=False)  # wb, ozon, yandex
    api_key = db.Column(db.String(255), nullable=False)      # для WB и Яндекс
    ozon_client_id = db.Column(db.String(100), nullable=True)   # для Ozon
    ozon_api_key = db.Column(db.String(200), nullable=True)     # для Ozon
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    user = db.relationship('User', backref=db.backref('api_keys', lazy=True))

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    article_slug = db.Column(db.String(200), nullable=False)
    author_name = db.Column(db.String(100), nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class Subscriber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class ReplyHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    marketplace = db.Column(db.String(50), nullable=False)
    review_text = db.Column(db.Text, nullable=False)
    reply_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    user = db.relationship('User', backref=db.backref('reply_history', lazy=True, order_by='ReplyHistory.created_at.desc()'))

# Класс Suggestion вынесен на правильный уровень
class Suggestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='new')  # Статус: new, reviewed, archived
    
    user = db.relationship('User', backref=db.backref('suggestions', lazy=True))