from app import db
from datetime import datetime

class Event(db.Model):
    __tablename__ = "events"

    # ---------------------------------------------------------
    # Colonnes principales
    # ---------------------------------------------------------
    id = db.Column(db.Integer, primary_key=True)

    # Titre de l'événement (obligatoire)
    title = db.Column(db.String(150), nullable=False)

    # Description optionnelle
    description = db.Column(db.Text, nullable=True)

    # Date et heure de l'événement
    date = db.Column(db.DateTime, nullable=False)

    # Capacité maximale de l'événement
    capacity = db.Column(db.Integer, nullable=False)

    # Date de création de l'événement
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # ---------------------------------------------------------
    # Relation : un event peut avoir plusieurs réservations
    # ---------------------------------------------------------
    # backref="event" → permet d'accéder à event depuis Booking
    # lazy=True → charge les réservations seulement quand nécessaire
    bookings = db.relationship("Booking", backref="event", lazy=True)

    # ---------------------------------------------------------
    # Méthode : calcul dynamique des places restantes
    # ---------------------------------------------------------
    def remaining_seats(self):
        """
        Calcule le nombre de places restantes pour cet événement.
        On compte le nombre total de réservations associées,
        puis on soustrait ce nombre de la capacité maximale.
        """
        from app.models.booking import Booking
        total_bookings = Booking.query.filter_by(event_id=self.id).count()
        return self.capacity - total_bookings

    # ---------------------------------------------------------
    # Méthode : conversion en dictionnaire (JSON-friendly)
    # ---------------------------------------------------------
    def to_dict(self):
        """
        Convertit l'objet Event en dictionnaire pour l'API.
        Inclut automatiquement les places restantes.
        """
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "date": self.date.isoformat(),  # format ISO → lisible + standard
            "capacity": self.capacity,
            "remaining_seats": self.remaining_seats(),
            "created_at": self.created_at.isoformat()
        }


   
