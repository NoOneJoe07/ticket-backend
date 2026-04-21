import os
from dotenv import load_dotenv

# Charger les variables du fichier .env
load_dotenv()

class Config:
    """Configuration de base (commune à Dev et Prod)."""

    SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev_jwt_secret")

    # Render fournit "postgres://" → SQLAlchemy exige "postgresql://"
    database_url = os.getenv("DATABASE_URL", "sqlite:///ticket_booking.db")
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = database_url

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # CORS
    CORS_HEADERS = "Content-Type"


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False

