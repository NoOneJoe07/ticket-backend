import os
from dotenv import load_dotenv

load_dotenv()

# Répertoire de base du backend (app/)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Répertoire instance/ à la racine du backend
INSTANCE_DIR = os.path.join(BASE_DIR, "..", "instance")

# Créer le dossier instance/ si absent
os.makedirs(INSTANCE_DIR, exist_ok=True)

class Config:
    """Configuration de base (commune à Dev et Prod)."""

    SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev_jwt_secret")

    # Si DATABASE_URL n'est pas défini → SQLite ABSOLU
    database_url = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(INSTANCE_DIR, 'ticket_booking.db')}"
    )

    # Correction Render postgres:// → postgresql://
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CORS_HEADERS = "Content-Type"


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False

