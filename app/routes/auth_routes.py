from flask import Blueprint, request, jsonify
from app import db, bcrypt
from app.models.user import User
import jwt
import datetime
from flask import current_app

# IMPORTS DES DÉCORATEURS DE SÉCURITÉ
# -----------------------------------
# token_required  → vérifie le JWT et injecte current_user
# admin_required  → vérifie que current_user.role == "admin"
from app.utils.auth_utils import token_required, admin_required

auth_bp = Blueprint("auth_bp", __name__)

# ---------------------------------------------------------
# REGISTER — Création d’un utilisateur
# ---------------------------------------------------------
@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Inscrit un nouvel utilisateur.
    Accessible publiquement (pas besoin de token).
    """
    data = request.get_json()

    # Vérification des champs obligatoires
    required_fields = ["fullname", "email", "password"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    fullname = data["fullname"]
    email = data["email"].lower()
    password = data["password"]

    # Vérifier si l'utilisateur existe déjà
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"error": "Email already registered"}), 409

    # Création de l'utilisateur
    new_user = User(fullname=fullname, email=email)
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "message": "User registered successfully",
        "user": new_user.to_dict()
    }), 201


# ---------------------------------------------------------
# LOGIN — Génération du JWT
# ---------------------------------------------------------
@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Authentifie un utilisateur et génère un JWT.
    Accessible publiquement.
    """
    data = request.get_json()

    if not data or "email" not in data or "password" not in data:
        return jsonify({"error": "Email and password are required"}), 400

    email = data["email"].lower()
    password = data["password"]

    user = User.query.filter_by(email=email).first()

    # Vérification email + mot de passe
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid email or password"}), 401

    # Génération du token JWT
    token = jwt.encode(
        {
            "user_id": user.id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
        },
        current_app.config["SECRET_KEY"],
        algorithm="HS256"
    )

    return jsonify({
        "message": "Login successful",
        "token": token,
        "user": user.to_dict()
    }), 200


# ---------------------------------------------------------
# ME — Retourne l'utilisateur connecté
# ---------------------------------------------------------
@auth_bp.route("/me", methods=["GET"])
@token_required
def me(current_user):
    """
    Retourne les informations de l'utilisateur connecté.
    Nécessite un JWT valide.
    """
    return jsonify({
        "user": current_user.to_dict()
    }), 200


# ---------------------------------------------------------
# ROUTE DE TEST — Non protégée
# ---------------------------------------------------------
@auth_bp.route("/test", methods=["GET"])
def test_auth():
    """
    Route de test simple pour vérifier que le blueprint fonctionne.
    """
    return jsonify({"message": "Auth route OK"}), 200



