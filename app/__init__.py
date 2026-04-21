from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from .config import DevelopmentConfig
from flask_talisman import Talisman

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)

    # Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    CORS(app)
    Talisman(app, content_security_policy=None)


    # IMPORT DES MODÈLES (OBLIGATOIRE POUR FLASK-MIGRATE)
    from app.models.user import User
    from app.models.event import Event
    from app.models.booking import Booking

    # Routes (blueprints)
    from app.routes.auth_routes import auth_bp
    from app.routes.event_routes import event_bp
    from app.routes.booking_routes import booking_bp
    from app.routes.payment_routes import payment_bp   # ← AJOUT ICI

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(event_bp, url_prefix="/events")
    app.register_blueprint(booking_bp, url_prefix="/bookings")
    app.register_blueprint(payment_bp, url_prefix="/payments")  # ← AJOUT ICI

    return app



