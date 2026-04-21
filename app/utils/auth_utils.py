import jwt
from flask import request, jsonify, current_app
from functools import wraps
from app.models.user import User

# ---------------------------------------------------------
#   Décorateur : token_required
# ---------------------------------------------------------
# Ce décorateur protège une route en exigeant un JWT valide.
# Il :
#   1. Vérifie la présence du header Authorization
#   2. Extrait le token "Bearer <token>"
#   3. Décode le JWT avec la SECRET_KEY
#   4. Vérifie l'expiration
#   5. Charge l'utilisateur depuis la base de données
#   6. Injecte current_user dans la route protégée
#
# Si quelque chose ne va pas → 401 Unauthorized
# ---------------------------------------------------------
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Vérifier si le header Authorization existe
        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]

            # Le format attendu est : "Bearer <token>"
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

        # Aucun token fourni
        if not token:
            return jsonify({"error": "Token missing"}), 401

        try:
            # Décodage du JWT
            data = jwt.decode(
                token,
                current_app.config["SECRET_KEY"],
                algorithms=["HS256"]
            )

            # Récupération de l'utilisateur
            current_user = User.query.get(data["user_id"])

        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401

        except Exception:
            return jsonify({"error": "Invalid token"}), 401

        # Injection de current_user dans la route protégée
        return f(current_user, *args, **kwargs)

    return decorated


# ---------------------------------------------------------
#   Décorateur : admin_required
# ---------------------------------------------------------
# Ce décorateur s'utilise APRÈS token_required.
# Il :
#   1. Vérifie que l'utilisateur est authentifié
#   2. Vérifie que son rôle est "admin"
#
# Si l'utilisateur n'est pas admin → 403 Forbidden
# ---------------------------------------------------------
def admin_required(f):
    @wraps(f)
    def decorated(current_user, *args, **kwargs):

        # Vérifier le rôle
        if current_user.role != "admin":
            return jsonify({"error": "Admin access required"}), 403

        return f(current_user, *args, **kwargs)

    return decorated

