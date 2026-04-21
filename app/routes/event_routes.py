from flask import Blueprint, request, jsonify
from app.utils.auth_utils import token_required, admin_required
from app import db
from app.models.event import Event
from datetime import datetime

event_bp = Blueprint("event_bp", __name__)

# ---------------------------------------------------------
# ROUTE DE TEST (protégée)
# ---------------------------------------------------------
@event_bp.route("/test", methods=["GET"])
@token_required
def test_event(current_user):
    return jsonify({
        "message": "Event route OK",
        "user": current_user.to_dict()
    }), 200


# ---------------------------------------------------------
# CREATE EVENT (ADMIN ONLY)
# ---------------------------------------------------------
@event_bp.route("/", methods=["POST"])
@token_required
@admin_required
def create_event(current_user):
    """
    Crée un nouvel événement.
    Accessible uniquement aux admins.
    """
    data = request.get_json()

    required_fields = ["title", "description", "date", "capacity"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    try:
        event_date = datetime.fromisoformat(data["date"])
    except:
        return jsonify({"error": "Invalid date format. Use ISO format."}), 400

    new_event = Event(
        title=data["title"],
        description=data["description"],
        date=event_date,
        capacity=data["capacity"]
    )

    db.session.add(new_event)
    db.session.commit()

    return jsonify({
        "message": "Event created successfully",
        "event": new_event.to_dict()
    }), 201


# ---------------------------------------------------------
# GET ALL EVENTS (USER + ADMIN)
# ---------------------------------------------------------
@event_bp.route("/", methods=["GET"])
@token_required
def get_events(current_user):
    """
    Retourne tous les événements.
    Accessible à tous les utilisateurs connectés.
    """
    events = Event.query.all()
    return jsonify([event.to_dict() for event in events]), 200


# ---------------------------------------------------------
# UPDATE EVENT (ADMIN ONLY)
# ---------------------------------------------------------
@event_bp.route("/<int:event_id>", methods=["PUT"])
@token_required
@admin_required
def update_event(current_user, event_id):
    """
    Permet à un ADMIN de modifier un événement.
    Champs modifiables :
    - title
    - description
    - date (ISO)
    - capacity (protégée)
    """
    event = Event.query.get(event_id)
    if not event:
        return jsonify({"error": "Event not found"}), 404

    data = request.get_json()

    # Mise à jour du titre
    if "title" in data:
        event.title = data["title"]

    # Mise à jour de la description
    if "description" in data:
        event.description = data["description"]

    # Mise à jour de la date
    if "date" in data:
        try:
            event.date = datetime.fromisoformat(data["date"])
        except:
            return jsonify({"error": "Invalid date format. Use ISO format."}), 400

    # Mise à jour de la capacité
    if "capacity" in data:
        new_capacity = data["capacity"]
        current_bookings = len(event.bookings)

        if new_capacity < current_bookings:
            return jsonify({
                "error": "Capacity cannot be lower than current number of bookings",
                "current_bookings": current_bookings
            }), 400

        event.capacity = new_capacity

    db.session.commit()

    return jsonify({
        "message": "Event updated successfully",
        "event": event.to_dict()
    }), 200


# ---------------------------------------------------------
# DELETE EVENT (ADMIN ONLY)
# ---------------------------------------------------------
@event_bp.route("/<int:event_id>", methods=["DELETE"])
@token_required
@admin_required
def delete_event(current_user, event_id):
    """
    Permet à un ADMIN de supprimer un événement.
    - Vérifie que l'événement existe
    - Empêche la suppression si des réservations existent
    """
    event = Event.query.get(event_id)

    if not event:
        return jsonify({"error": "Event not found"}), 404

    if len(event.bookings) > 0:
        return jsonify({
            "error": "Cannot delete event with existing bookings",
            "current_bookings": len(event.bookings)
        }), 400

    db.session.delete(event)
    db.session.commit()

    return jsonify({
        "message": "Event deleted successfully",
        "event_id": event_id
    }), 200

