from flask import Blueprint, request, jsonify
from app.utils.auth_utils import token_required
from app import db
from app.models.booking import Booking
from app.models.event import Event

# Import du générateur automatique de plan de salle
from app.utils.seat_map import generate_seat_map
from app.utils.auth_utils import token_required, admin_required

# -----------------------------------------
# Blueprint des routes "bookings"
# -----------------------------------------
booking_bp = Blueprint("booking_bp", __name__)

# -----------------------------------------
# Route de test (protégée)
# -----------------------------------------
@booking_bp.route("/test", methods=["GET"])
@token_required
def test_booking(current_user):
    """
    Vérifie que les routes booking fonctionnent
    et que l'utilisateur est bien authentifié.
    """
    return jsonify({
        "message": "Booking route OK",
        "user": current_user.to_dict()
    }), 200


# -----------------------------------------
# CREATE BOOKING (USER ONLY)
# -----------------------------------------
@booking_bp.route("/", methods=["POST"])
@token_required
def create_booking(current_user):
    """
    Crée une réservation pour un événement avec sélection de siège.
    Empêche les doublons et respecte la capacité de l'événement.
    """
    data = request.get_json()

    # Vérification des champs obligatoires
    required_fields = ["event_id", "seat_number"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    event_id = data["event_id"]
    seat_number = data["seat_number"]

    # Vérifier que l'événement existe
    event = Event.query.get(event_id)
    if not event:
        return jsonify({"error": "Event not found"}), 404

    # Vérifier la capacité restante
    if event.remaining_seats() <= 0:
        return jsonify({"error": "Event is fully booked"}), 400

    # Vérifier si le siège est déjà réservé
    existing_seat = Booking.query.filter_by(
        event_id=event.id,
        seat_number=seat_number
    ).first()

    if existing_seat:
        return jsonify({"error": "Seat already taken"}), 400

    # Créer la réservation
    new_booking = Booking(
        user_id=current_user.id,
        event_id=event.id,
        seat_number=seat_number
    )

    db.session.add(new_booking)
    db.session.commit()

    return jsonify({
        "message": "Booking created successfully",
        "booking": new_booking.to_dict()
    }), 201


# -----------------------------------------
# GET USER BOOKINGS (USER ONLY)
# -----------------------------------------
@booking_bp.route("/mine", methods=["GET"])
@token_required
def get_my_bookings(current_user):
    """
    Retourne toutes les réservations de l'utilisateur connecté.
    """
    bookings = Booking.query.filter_by(user_id=current_user.id).all()
    return jsonify([b.to_dict() for b in bookings]), 200


# -----------------------------------------
# CANCEL BOOKING (USER ONLY)
# -----------------------------------------
@booking_bp.route("/<int:booking_id>", methods=["DELETE"])
@token_required
def cancel_booking(current_user, booking_id):
    """
    Permet à un utilisateur d'annuler sa propre réservation.
    """
    booking = Booking.query.get(booking_id)

    if not booking:
        return jsonify({"error": "Booking not found"}), 404

    # Vérifier que la réservation appartient à l'utilisateur
    if booking.user_id != current_user.id:
        return jsonify({"error": "You cannot cancel someone else's booking"}), 403

    db.session.delete(booking)
    db.session.commit()

    return jsonify({"message": "Booking cancelled successfully"}), 200


# -----------------------------------------
# GET OCCUPIED SEATS FOR AN EVENT (USER ONLY)
# -----------------------------------------
@booking_bp.route("/occupied/<int:event_id>", methods=["GET"])
@token_required
def get_occupied_seats(current_user, event_id):
    """
    Retourne la liste des sièges déjà réservés pour un événement.
    Utile pour afficher les sièges occupés dans le frontend.
    """
    bookings = Booking.query.filter_by(event_id=event_id).all()
    seats = [b.seat_number for b in bookings]

    return jsonify({
        "event_id": event_id,
        "occupied_seats": seats
    }), 200


# -----------------------------------------
# GET FULL SEAT MAP (AUTO-GENERATED)
# -----------------------------------------
@booking_bp.route("/seatmap/<int:event_id>", methods=["GET"])
@token_required
def get_seat_map(current_user, event_id):
    """
    Retourne :
    - le plan de salle complet (généré automatiquement)
    - les sièges occupés
    - les sièges disponibles

    Permet au frontend d'afficher un plan visuel complet.
    """
    event = Event.query.get(event_id)
    if not event:
        return jsonify({"error": "Event not found"}), 404

    # Génération automatique du plan de salle (A1–A10, B1–B10, etc.)
    full_map = generate_seat_map(rows=10, seats_per_row=10)

    # Sièges déjà réservés
    bookings = Booking.query.filter_by(event_id=event_id).all()
    occupied = [b.seat_number for b in bookings]

    # Sièges disponibles
    available = [seat for seat in full_map if seat not in occupied]

    return jsonify({
        "event_id": event_id,
        "seat_map": full_map,
        "occupied_seats": occupied,
        "available_seats": available
    }), 200

# -----------------------------------------
# ADMIN : GET ALL BOOKINGS FOR AN EVENT
# -----------------------------------------
@booking_bp.route("/event/<int:event_id>/all", methods=["GET"])
@admin_required
def admin_get_event_bookings(current_user, event_id):
    """
    Route ADMIN-ONLY.
    Retourne toutes les réservations d'un événement :
    - utilisateur
    - siège
    - statut
    - date
    """
    event = Event.query.get(event_id)
    if not event:
        return jsonify({"error": "Event not found"}), 404

    bookings = Booking.query.filter_by(event_id=event_id).all()

    return jsonify({
        "event": event.to_dict(),
        "total_bookings": len(bookings),
        "bookings": [b.to_dict() for b in bookings]
    }), 200

# -----------------------------------------
# UPDATE BOOKING (CHANGE SEAT) — USER ONLY
# -----------------------------------------
@booking_bp.route("/<int:booking_id>", methods=["PUT"])
@token_required
def update_booking(current_user, booking_id):
    """
    Permet à un utilisateur de modifier sa réservation :
    - changer de siège
    - vérifier que le nouveau siège est libre
    - vérifier que la réservation lui appartient
    """
    data = request.get_json()

    # Vérifier que seat_number est fourni
    if "seat_number" not in data:
        return jsonify({"error": "Missing field: seat_number"}), 400

    new_seat = data["seat_number"]

    # Récupérer la réservation
    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({"error": "Booking not found"}), 404

    # Vérifier que la réservation appartient à l'utilisateur
    if booking.user_id != current_user.id:
        return jsonify({"error": "You cannot modify someone else's booking"}), 403

    # Récupérer l'événement associé
    event = Event.query.get(booking.event_id)

    # Vérifier si le nouveau siège est déjà pris
    seat_taken = Booking.query.filter_by(
        event_id=event.id,
        seat_number=new_seat
    ).first()

    if seat_taken:
        return jsonify({"error": "Seat already taken"}), 400

    # Mise à jour du siège
    booking.seat_number = new_seat
    db.session.commit()

    return jsonify({
        "message": "Booking updated successfully",
        "booking": booking.to_dict()
    }), 200
