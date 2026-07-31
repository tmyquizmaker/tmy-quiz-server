import re
from datetime import datetime
import requests
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
    """Envoie l'e-mail de vérification via l'API HTTP de Brevo (Port 443 - Garanti sans blocage)."""
    token = _get_serializer().dumps(user.email, salt=current_app.config["SECURITY_PASSWORD_SALT"])
    lien = f"{current_app.config['APP_BASE_URL']}/auth/verify-email/{token}"

    url = "https://api.brevo.com/v3/smtp/email"
    
    headers = {
        "accept": "application/json",
        "api-key": current_app.config.get("MAIL_PASSWORD"),
        "content-type": "application/json"
    }
    
    payload = {
        "sender": {"email": current_app.config.get("MAIL_DEFAULT_SENDER"), "name": "TMY Quiz Maker"},
        "to": [{"email": user.email, "name": f"{user.prenom} {user.nom}"}],
        "subject": "Confirmez votre inscription à TMY Quiz Maker",
        "htmlContent": f"""
            <!DOCTYPE html>
            <html lang="fr">
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: Arial, sans-serif; background-color: #f4f6f8; margin: 0; padding: 20px; }}
                    .container {{ max-width: 600px; background: #ffffff; padding: 30px; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }}
                    h2 {{ color: #2c3e50; }}
                    p {{ color: #555555; line-height: 1.5; }}
                    .btn {{ display: inline-block; background-color: #0d9488; color: #ffffff !important; text-decoration: none; padding: 12px 24px; border-radius: 6px; font-weight: bold; margin: 20px 0; }}
                    .footer {{ font-size: 12px; color: #999999; margin-top: 30px; border-top: 1px solid #eeeeee; padding-top: 15px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h2>Bienvenue sur TMY Quiz Maker, {user.prenom} !</h2>
                    <p>Merci de vous être inscrit. Pour sécuriser votre compte et accéder à toutes les fonctionnalités, veuillez valider votre adresse e-mail en cliquant sur le bouton ci-dessous :</p>
                    
                    <a href="{lien}" class="btn" target="_blank">Valider mon adresse e-mail</a>
                    
                    <p>Si le bouton ne fonctionne pas, copiez et collez ce lien dans votre navigateur :<br><a href="{lien}">{lien}</a></p>
                    
                    <div class="footer">
                        <p>Ce lien est valable 24 heures. Si vous n'avez pas demandé la création de ce compte, veuillez ignorer cet e-mail.</p>
                    </div>
                </div>
            </body>
            </html>
        """
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code in [200, 201, 202]:
            current_app.logger.info("📧 E-mail de vérification envoyé avec succès via l'API HTTP Brevo à %s", user.email)
            return True
        else:
            current_app.logger.error("❌ ÉCHEC API BREVO : %s", response.text)
            return False
    except Exception as exc:
        current_app.logger.error("❌ ERREUR REQUÊTE API BREVO pour %s : %s", user.email, exc)
        return False


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

    mail_envoye = _send_verification_email(user)

    if not mail_envoye:
        return jsonify({
            "message": "Compte créé, mais l'e-mail de vérification n'a pas pu être envoyé. "
                       "Vérifiez vos logs Render ou demandez un renvoi d'e-mail.",
            "user": user.to_public_dict(),
        }), 201

    return jsonify({
        "message": "Compte créé avec succès. Vérifiez votre boîte mail pour valider votre adresse.",
        "user": user.to_public_dict(),
    }), 201


@auth_bp.route("/resend-verification", methods=["POST"])
def resend_verification():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()

    if not email:
        return jsonify({"error": "Adresse e-mail requise"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Aucun compte associé à cet e-mail"}), 404

    if user.email_verified:
        return jsonify({"message": "Votre e-mail est déjà vérifié. Vous pouvez vous connecter."}), 200

    mail_envoye = _send_verification_email(user)
    if mail_envoye:
        return jsonify({"message": "Un nouvel e-mail de confirmation a été envoyé."}), 200
    else:
        return jsonify({"error": "Impossible d'envoyer l'e-mail pour le moment. Réessayez plus tard."}), 500


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
    identifiant = (data.get("identifiant") or "").strip()
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
    reponse_generique = {
        "message": "Si un compte existe avec cet email, un lien de réinitialisation a été envoyé."
    }
    if not user:
        return jsonify(reponse_generique), 200

    token = _get_serializer().dumps(user.email, salt=current_app.config["SECURITY_PASSWORD_SALT"] + "-reset")
    lien = f"{current_app.config['APP_BASE_URL']}/auth/reset-password/{token}"

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
            max_age=3600,
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


@auth_bp.route("/avatar", methods=["POST"])
@jwt_required()
def upload_avatar():
    data = request.get_json(silent=True) or {}
    avatar_base64 = data.get("avatar_base64")

    if not avatar_base64:
        return jsonify({"error": "Image manquante"}), 400

    if len(avatar_base64) > 700_000:
        return jsonify({"error": "Image trop volumineuse"}), 400

    user = User.query.get(get_jwt_identity())
    if not user:
        return jsonify({"error": "Utilisateur introuvable"}), 404

    user.avatar_base64 = avatar_base64
    db.session.commit()

    return jsonify({"message": "Photo de profil mise à jour.", "user": user.to_public_dict()}), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user = User.query.get(get_jwt_identity())
    if not user:
        return jsonify({"error": "Utilisateur introuvable"}), 404
    return jsonify(user.to_public_dict()), 200