import os
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from werkzeug.security import generate_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Si us plau, inicia sessió per accedir.'


def create_app():
    flask_app = Flask(__name__)
    flask_app.wsgi_app = ProxyFix(flask_app.wsgi_app, x_for=1, x_proto=1)

    flask_app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'clau-per-defecte')
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL', 'sqlite:////app/data/pinyator.db?timeout=20'
    )
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(flask_app)
    login_manager.init_app(flask_app)

    from app.routes.auth import auth_bp
    from app.routes.events import events_bp
    from app.routes.attendance import attendance_bp
    from app.routes.castells import castells_bp
    from app.routes.templates import templates_bp

    flask_app.register_blueprint(auth_bp)
    flask_app.register_blueprint(events_bp)
    flask_app.register_blueprint(attendance_bp)
    flask_app.register_blueprint(castells_bp)
    flask_app.register_blueprint(templates_bp)

    @flask_app.context_processor
    def inject_now():
        return {'now': datetime.now()}

    with flask_app.app_context():
        import app.models
        db.create_all()
        from app.seeds import seed_all
        seed_all()

    return flask_app


@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))
