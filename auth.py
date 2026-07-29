import re
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from sqlalchemy import or_

from extensions import db, bcrypt, mail
from models import User

auth_bp = Blueprint("auth", __name__)

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _get_serializer():
    return URLSafeTimedSerializer(current_app.config["JWT_SECRET_KEY"])


def _send_verification_email(user):
    token = _get_serializer().dumps(user.email, salt=current_app.config["SECURITY_PASSWORD_SALT"])
    lien = f"{current_app.config['APP_BASE_URL']}/verify-email/{token}"

    msg = Message(
        subject="Vérifiez votre adresse email",
        recipients=[user.email],
        body=(
            f"Bonjour {user.prenom},\n\n"
            f"Confirmez votre inscription en cliquant sur ce lien "
            f"(valable 24h) :\n{lien}\n\n"
            "Si vous n'êtes pas à l'origine de cette demande, ignorez ce message."
        ),
    )
    mail.send(msg)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}

    required_fields = ["nom", "prenom", "username", "date_naissance", "email", "password"]
    missing = [f for f in required_fields if not data.get(f)]
    if missing:
        return jsonify({"error": f"Champs manquants : {', '.join(missing)}"}), 400

    email = data["email"].strip().lower()
    username = data["username"].strip()

    if not EMAIL_REGEX.match(email):
        return jsonify({"error": "Adresse email invalide"}), 400

    if len(data["password"]) < 8:
        return jsonify({"error": "Le mot de passe doit contenir au moins 8 caractères"}), 400

    try:
        date_naissance = datetime.strptime(data["date_naissance"], "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Format de date de naissance invalide (attendu AAAA-MM-JJ)"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Cet email est déjà utilisé"}), 409
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Ce nom d'utilisateur est déjà pris"}), 409

    password_hash = bcrypt.generate_password_hash(data["password"]).decode("utf-8")

    user = User(
        nom=data["nom"].strip(),
        prenom=data["prenom"].strip(),
        username=username,
        date_naissance=date_naissance,
        email=email,
        password_hash=password_hash,
        email_verified=False,
    )
    db.session.add(user)
    db.session.commit()

    try:
        _send_verification_email(user)
    except Exception as exc:  # noqa: BLE001 - on ne bloque pas l'inscription si le mail échoue
        current_app.logger.error("Échec d'envoi de l'email de vérification: %s", exc)
        return jsonify({
            "message": "Compte créé, mais l'email de vérification n'a pas pu être envoyé. "
                       "Contactez le support ou redemandez un renvoi.",
            "user": user.to_public_dict(),
        }), 201

    return jsonify({
        "message": "Compte créé. Vérifiez votre boîte mail pour valider votre adresse.",
        "user": user.to_public_dict(),
    }), 201


def _html_page(titre, message, succes=True):
    couleur = "#1a7f37" if succes else "#c0392b"
    return f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="utf-8">
        <title>{titre}</title>
        <style>
            body {{ font-family: sans-serif; text-align: center; padding: 60px 20px; }}
            h1 {{ color: {couleur}; }}
        </style>
    </head>
    <body>
        <h1>{titre}</h1>
        <p>{message}</p>
        <p>Vous pouvez fermer cette page et retourner dans l'application.</p>
    </body>
    </html>
    """


@auth_bp.route("/verify-email/<token>", methods=["GET"])
def verify_email(token):
    try:
        email = _get_serializer().loads(
            token,
            salt=current_app.config["SECURITY_PASSWORD_SALT"],
            max_age=current_app.config["EMAIL_TOKEN_MAX_AGE_SECONDS"],
        )
    except SignatureExpired:
        return _html_page("Lien expiré", "Ce lien de vérification a expiré. Redemandez-en un depuis l'application.", succes=False), 400
    except BadSignature:
        return _html_page("Lien invalide", "Ce lien de vérification n'est pas valide.", succes=False), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return _html_page("Utilisateur introuvable", "Aucun compte ne correspond à ce lien.", succes=False), 404

    if not user.email_verified:
        user.email_verified = True
        db.session.commit()

    return _html_page("Email vérifié", "Votre adresse email a bien été confirmée. Vous pouvez vous connecter dans l'application."), 200


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    identifiant = (data.get("identifiant") or "").strip()  # username OU email
    password = data.get("password") or ""

    if not identifiant or not password:
        return jsonify({"error": "Identifiant et mot de passe requis"}), 400

    user = User.query.filter(
        or_(User.username == identifiant, User.email == identifiant.lower())
    ).first()

    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        return jsonify({"error": "Identifiant ou mot de passe incorrect"}), 401

    if not user.email_verified:
        return jsonify({"error": "Merci de vérifier votre email avant de vous connecter"}), 403

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": user.to_public_dict(),
    }), 200


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """Le client (desktop/mobile) appelle ceci avec le refresh_token quand
    l'access_token expire, pour éviter de redemander le mot de passe."""
    identity = get_jwt_identity()
    new_access_token = create_access_token(identity=identity)
    return jsonify({"access_token": new_access_token}), 200


@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()

    if not email:
        return jsonify({"error": "Email requis"}), 400

    user = User.query.filter_by(email=email).first()
    # Réponse identique que l'utilisateur existe ou non, pour ne pas
    # révéler quels emails sont enregistrés dans le système.
    reponse_generique = {
        "message": "Si un compte existe avec cet email, un lien de réinitialisation a été envoyé."
    }
    if not user:
        return jsonify(reponse_generique), 200

    token = _get_serializer().dumps(user.email, salt=current_app.config["SECURITY_PASSWORD_SALT"] + "-reset")
    lien = f"{current_app.config['APP_BASE_URL']}/reset-password/{token}"

    try:
        msg = Message(
            subject="Réinitialisation de votre mot de passe",
            recipients=[user.email],
            body=(
                f"Bonjour {user.prenom},\n\n"
                f"Cliquez sur ce lien pour choisir un nouveau mot de passe (valable 1h) :\n{lien}\n\n"
                "Si vous n'êtes pas à l'origine de cette demande, ignorez ce message."
            ),
        )
        mail.send(msg)
    except Exception as exc:  # noqa: BLE001
        current_app.logger.error("Échec d'envoi de l'email de réinitialisation: %s", exc)

    return jsonify(reponse_generique), 200


@auth_bp.route("/reset-password/<token>", methods=["GET"])
def reset_password_form(token):
    """Petite page HTML avec un formulaire pour saisir le nouveau mot de passe,
    qui soumet en JS vers POST /reset-password/<token> (API ci-dessous)."""
    return f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head><meta charset="utf-8"><title>Nouveau mot de passe</title></head>
    <body style="font-family: sans-serif; max-width: 400px; margin: 60px auto;">
        <h1>Choisissez un nouveau mot de passe</h1>
        <input id="pwd" type="password" placeholder="Nouveau mot de passe (8 caractères min.)" style="width:100%; padding:8px;">
        <button onclick="soumettre()" style="margin-top:10px; padding:8px 16px;">Valider</button>
        <p id="resultat"></p>
        <script>
            async function soumettre() {{
                const pwd = document.getElementById('pwd').value;
                const res = await fetch(window.location.pathname, {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{password: pwd}})
                }});
                const data = await res.json();
                document.getElementById('resultat').textContent = data.message || data.error;
            }}
        </script>
    </body>
    </html>
    """


@auth_bp.route("/reset-password/<token>", methods=["POST"])
def reset_password_submit(token):
    data = request.get_json(silent=True) or {}
    nouveau_mdp = data.get("password") or ""

    if len(nouveau_mdp) < 8:
        return jsonify({"error": "Le mot de passe doit contenir au moins 8 caractères"}), 400

    try:
        email = _get_serializer().loads(
            token,
            salt=current_app.config["SECURITY_PASSWORD_SALT"] + "-reset",
            max_age=3600,  # 1h
        )
    except SignatureExpired:
        return jsonify({"error": "Ce lien a expiré, refaites une demande"}), 400
    except BadSignature:
        return jsonify({"error": "Lien invalide"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Utilisateur introuvable"}), 404

    user.password_hash = bcrypt.generate_password_hash(nouveau_mdp).decode("utf-8")
    db.session.commit()

    return jsonify({"message": "Mot de passe mis à jour avec succès."}), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user = User.query.get(get_jwt_identity())
    if not user:
        return jsonify({"error": "Utilisateur introuvable"}), 404
    return jsonify(user.to_public_dict()), 200
