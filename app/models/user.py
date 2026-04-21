from app import db, bcrypt
from datetime import datetime

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="user")  # user / admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relation : un user peut avoir plusieurs réservations
    bookings = db.relationship("Booking", backref="user", lazy=True)

    # Méthodes utilitaires
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "fullname": self.fullname,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at.isoformat()
        }
