from app import db
from datetime import datetime

class Booking(db.Model):
    __tablename__ = "bookings"

    # ---------------------------------------------------------
    # Colonnes principales
    # ---------------------------------------------------------
    id = db.Column(db.Integer, primary_key=True)

    # L'utilisateur qui a réservé
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # L'événement réservé
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=False)

    # Statut de la réservation (confirmed / cancelled)
    status = db.Column(db.String(20), default="confirmed")

    # Date de création de la réservation
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # ---------------------------------------------------------
    # Sélection de siège
    # ---------------------------------------------------------
    # Chaque réservation doit avoir un siège unique pour un event.
    # Exemple : "A5", "B12", "VIP-03"
    seat_number = db.Column(db.String(10), nullable=False)

    # ---------------------------------------------------------
    # Méthode : conversion en dictionnaire (JSON-friendly)
    # ---------------------------------------------------------
    def to_dict(self):
        """
        Convertit l'objet Booking en dictionnaire pour l'API.
        Inclut le siège réservé.
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "event_id": self.event_id,
            "seat_number": self.seat_number,
            "status": self.status,
            "created_at": self.created_at.isoformat()
        }

