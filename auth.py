import random
import re
import uuid
from datetime import datetime, timedelta
import requests
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required,
    get_jwt_identity, get_jwt,
)
from sqlalchemy import or_

from extensions import db, bcrypt, jwt
from models import User, VerificationCode

auth_bp = Blueprint("auth", __name__)

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


# ==========================================================
# Connexion unique : un compte ne peut être connecté que sur UN SEUL
# appareil à la fois. Chaque login génère un nouvel identifiant de
# session ("sid") stocké dans le JWT ET en base sur l'utilisateur. Si
# les deux ne correspondent plus (parce qu'un login plus récent a eu
# lieu ailleurs), le token est considéré révoqué automatiquement.
# ==========================================================

@jwt.token_in_blocklist_loader
def _verifier_session_unique(jwt_header, jwt_payload):
    token_sid = jwt_payload.get("sid")
    identity = jwt_payload.get("sub")
    if not token_sid or not identity:
        return True  # token mal formé : traité comme révoqué par sécurité

    user = User.query.get(int(identity))
    if not user:
        return True

    return token_sid != user.current_session_id


@jwt.revoked_token_loader
def _token_revoque(jwt_header, jwt_payload):
    return jsonify({
        "error": "Votre session a expiré : ce compte a été connecté sur un autre appareil."
    }), 401


# ==========================================================
# Envoi d'email via l'API HTTP de Brevo (port 443 - fiable,
# fonctionne même quand le SMTP classique est bloqué)
# ==========================================================

def _envoyer_via_brevo(destinataire_email, destinataire_nom, sujet, html_content):
    url = "https://api.brevo.com/v3/smtp/email"

    headers = {
        "accept": "application/json",
        "api-key": current_app.config.get("MAIL_PASSWORD"),
        "content-type": "application/json",
    }

    payload = {
        "sender": {"email": current_app.config.get("MAIL_DEFAULT_SENDER"), "name": "TMY Quiz Maker"},
        "to": [{"email": destinataire_email, "name": destinataire_nom}],
        "subject": sujet,
        "htmlContent": html_content,
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code in [200, 201, 202]:
            current_app.logger.info("📧 Email envoyé avec succès via l'API HTTP Brevo à %s", destinataire_email)
            return True
        current_app.logger.error("❌ ÉCHEC API BREVO : %s", response.text)
        return False
    except Exception as exc:
        current_app.logger.error("❌ ERREUR REQUÊTE API BREVO pour %s : %s", destinataire_email, exc)
        return False


def _email_template(titre_interieur, contenu_html):
    """Gabarit d'email professionnel réutilisé partout : en-tête sombre avec logo,
    corps clair, pied de page. Le logo vient de EMAIL_LOGO_URL (config/variable
    d'environnement) — doit être une URL publique (ex: image hébergée sur GitHub),
    un email ne peut pas charger un fichier local sur votre disque."""
    logo_url = current_app.config.get("EMAIL_LOGO_URL", "")
    logo_html = (
        f'<img src="{logo_url}" alt="TMY Quiz Maker" style="height:48px;">'
        if logo_url else
        '<span style="font-size:22px;font-weight:bold;color:#2dd4bf;">TMY QUIZ MAKER</span>'
    )

    return f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #f4f6f8; margin: 0; padding: 20px; }}
            .container {{ max-width: 520px; margin: auto; background: #ffffff; border-radius: 10px;
                          overflow: hidden; box-shadow: 0 4px 14px rgba(0,0,0,0.06); }}
            .header {{ background-color: #0f172a; padding: 24px; text-align: center; }}
            .body {{ padding: 32px 30px; }}
            h2 {{ color: #0f172a; margin-top: 0; }}
            p {{ color: #4b5563; line-height: 1.6; font-size: 14px; }}
            .code-box {{ font-size: 32px; font-weight: bold; letter-spacing: 8px; text-align: center;
                background: #f1f5f9; color: #0d9488; padding: 18px; border-radius: 8px; margin: 24px 0; }}
            .footer {{ font-size: 12px; color: #9ca3af; padding: 20px 30px; border-top: 1px solid #eeeeee; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">{logo_html}</div>
            <div class="body">
                <h2>{titre_interieur}</h2>
                {contenu_html}
            </div>
            <div class="footer">
                <p>TMY Quiz Maker — Smart Learning &amp; Party Experience</p>
                <p>Si vous n'êtes pas à l'origine de cette demande, ignorez cet e-mail en toute sécurité.</p>
            </div>
        </div>
    </body>
    </html>
    """


# ==========================================================
# Codes à 6 chiffres (vérification email + réinitialisation mdp)
# ==========================================================

def _generer_code():
    return f"{random.randint(0, 999999):06d}"


def _creer_code(user, purpose, minutes_validite=15):
    code = _generer_code()
    code_hash = bcrypt.generate_password_hash(code).decode("utf-8")
    entree = VerificationCode(
        user_id=user.id,
        code_hash=code_hash,
        purpose=purpose,
        expires_at=datetime.utcnow() + timedelta(minutes=minutes_validite),
    )
    db.session.add(entree)
    db.session.commit()
    return code


def _verifier_code(user, purpose, code):
    entree = (
        VerificationCode.query.filter_by(user_id=user.id, purpose=purpose, used=False)
        .order_by(VerificationCode.created_at.desc())
        .first()
    )
    if not entree or entree.expires_at < datetime.utcnow():
        return False
    if not bcrypt.check_password_hash(entree.code_hash, code):
        return False
    entree.used = True
    db.session.commit()
    return True


# ==========================================================
# Inscription & vérification d'email (par code)
# ==========================================================

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

    code = _creer_code(user, "verify_email")
    html = _email_template(
        f"Bienvenue, {user.prenom} !",
        f"""
        <p>Merci de vous être inscrit sur TMY Quiz Maker. Voici votre code de vérification, valable 15 minutes :</p>
        <div class="code-box">{code}</div>
        <p>Entrez ce code dans l'application pour activer votre compte.</p>
        """,
    )
    mail_envoye = _envoyer_via_brevo(user.email, f"{user.prenom} {user.nom}", "Votre code de vérification - TMY Quiz Maker", html)

    if not mail_envoye:
        return jsonify({
            "message": "Compte créé, mais l'e-mail n'a pas pu être envoyé. Redemandez un code depuis l'application.",
            "user": user.to_public_dict(),
        }), 201

    return jsonify({
        "message": "Compte créé. Entrez le code reçu par email pour l'activer.",
        "user": user.to_public_dict(),
    }), 201


@auth_bp.route("/verify-email-with-code", methods=["POST"])
def verify_email_with_code():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    code = (data.get("code") or "").strip()

    if not email or not code:
        return jsonify({"error": "Email et code requis"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Code invalide ou expiré"}), 400

    if user.email_verified:
        return jsonify({"message": "Votre email est déjà vérifié. Vous pouvez vous connecter."}), 200

    if not _verifier_code(user, "verify_email", code):
        return jsonify({"error": "Code invalide ou expiré"}), 400

    user.email_verified = True
    db.session.commit()

    return jsonify({"message": "Email vérifié avec succès. Vous pouvez vous connecter."}), 200


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

    code = _creer_code(user, "verify_email")
    html = _email_template(
        "Nouveau code de vérification",
        f"""<p>Voici votre nouveau code, valable 15 minutes :</p><div class="code-box">{code}</div>""",
    )
    if _envoyer_via_brevo(user.email, f"{user.prenom} {user.nom}", "Votre code de vérification - TMY Quiz Maker", html):
        return jsonify({"message": "Un nouveau code a été envoyé."}), 200
    return jsonify({"error": "Impossible d'envoyer l'e-mail pour le moment. Réessayez plus tard."}), 500


# ==========================================================
# Connexion & session
# ==========================================================

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

    # Nouvelle session : écrase l'ancienne, ce qui invalide automatiquement
    # le token de tout appareil précédemment connecté sur ce compte.
    nouveau_sid = uuid.uuid4().hex
    user.current_session_id = nouveau_sid
    db.session.commit()

    claims = {"sid": nouveau_sid}
    access_token = create_access_token(identity=str(user.id), additional_claims=claims)
    refresh_token = create_refresh_token(identity=str(user.id), additional_claims=claims)

    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": user.to_public_dict(),
    }), 200


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    # Le nouvel access_token garde le même sid que le refresh_token utilisé,
    # pour rester cohérent avec la session enregistrée sur le compte.
    sid = get_jwt().get("sid")
    new_access_token = create_access_token(identity=identity, additional_claims={"sid": sid})
    return jsonify({"access_token": new_access_token}), 200


# ==========================================================
# Mot de passe oublié (par code)
# ==========================================================

@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()

    if not email:
        return jsonify({"error": "Email requis"}), 400

    reponse_generique = {
        "message": "Si un compte existe avec cet email, un code de réinitialisation a été envoyé."
    }

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify(reponse_generique), 200

    code = _creer_code(user, "reset_password")
    html = _email_template(
        "Réinitialisation de votre mot de passe",
        f"""
        <p>Voici votre code de vérification, valable 15 minutes :</p>
        <div class="code-box">{code}</div>
        <p>Si vous n'êtes pas à l'origine de cette demande, ignorez cet e-mail.</p>
        """,
    )
    _envoyer_via_brevo(user.email, f"{user.prenom} {user.nom}", "Votre code de réinitialisation - TMY Quiz Maker", html)

    return jsonify(reponse_generique), 200


@auth_bp.route("/reset-password-with-code", methods=["POST"])
def reset_password_with_code():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    code = (data.get("code") or "").strip()
    nouveau_mdp = data.get("password") or ""

    if not email or not code or not nouveau_mdp:
        return jsonify({"error": "Email, code et nouveau mot de passe requis"}), 400

    if len(nouveau_mdp) < 8:
        return jsonify({"error": "Le mot de passe doit contenir au moins 8 caractères"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Code invalide ou expiré"}), 400

    if not _verifier_code(user, "reset_password", code):
        return jsonify({"error": "Code invalide ou expiré"}), 400

    user.password_hash = bcrypt.generate_password_hash(nouveau_mdp).decode("utf-8")
    db.session.commit()

    return jsonify({"message": "Mot de passe mis à jour avec succès."}), 200


# ==========================================================
# Photo de profil & informations du compte
# ==========================================================

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
