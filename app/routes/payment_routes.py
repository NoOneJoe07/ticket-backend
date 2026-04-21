from flask import Blueprint, request, jsonify
from app.utils.auth_utils import token_required
from app import db
from app.models.booking import Booking
import random

payment_bp = Blueprint("payment_bp", __name__)

# ---------------------------------------------------------
# SIMULATE PAYMENT (USER ONLY)
# ---------------------------------------------------------
@payment_bp.route("/simulate", methods=["POST"])
@token_required
def simulate_payment(current_user):
    """
    Simule un paiement pour une réservation.
    - 80% de chance de succès
    - Met à jour le statut de la réservation
    """
    data = request.get_json()

    if "booking_id" not in data:
        return jsonify({"error": "Missing field: booking_id"}), 400

    booking = Booking.query.get(data["booking_id"])

    if not booking:
        return jsonify({"error": "Booking not found"}), 404

    # Vérifier que la réservation appartient à l'utilisateur
    if booking.user_id != current_user.id:
        return jsonify({"error": "You cannot pay for someone else's booking"}), 403

    # Simuler un paiement (80% de réussite)
    payment_success = random.random() < 0.8

    if payment_success:
        booking.status = "paid"
        db.session.commit()
        return jsonify({
            "message": "Payment successful",
            "booking": booking.to_dict()
        }), 200

    else:
        booking.status = "payment_failed"
        db.session.commit()
        return jsonify({
            "message": "Payment failed",
            "booking": booking.to_dict()
        }), 400
