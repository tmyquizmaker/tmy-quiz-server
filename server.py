"""
===========================================
TMY Quiz Maker - Serveur WebSocket Central
===========================================
"""

# ⚠️ IMPORTANT : ce patch doit être fait EN TOUT PREMIER, avant tout autre
# import (y compris `os`, `requests`, `flask`, etc.). S'il est fait trop tard,
# ou si gunicorn le fait après qu'un module ait déjà importé `ssl`/`socket`,
# on obtient une erreur "maximum recursion depth exceeded" sur les appels
# HTTPS (comme l'envoi d'email via l'API Brevo).
from gevent import monkey
monkey.patch_all()

import os
import random
import threading

from flask import Flask, request
from flask_migrate import Migrate
from flask_socketio import SocketIO, emit, join_room
from datetime import timedelta
from sqlalchemy import text

# 1. Importation de l'instance DB partagée depuis extensions.py
from extensions import db, bcrypt, jwt, mail

# Blueprints d'authentification et de scores
from auth import auth_bp
from scores import scores_bp

# Importation depuis le sous-dossier ai/
from ai.ai_generator import AIGenerator

app = Flask(__name__)

# ========================================================
# ⚙️ CONFIGURATION BASE DE DONNÉES & MIGRATIONS
# ========================================================
# Utilise la variable d'environnement DATABASE_URL (Neon/Render) ou bascule sur un fichier local
database_url = os.environ.get("DATABASE_URL", "sqlite:///local_fallback.db")
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Évite les erreurs "SSL connection has been closed unexpectedly" avec les bases
# hébergées (Render/Neon) qui coupent les connexions inactives : SQLAlchemy vérifie
# la connexion avant chaque requête et en ouvre une nouvelle si besoin.
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_pre_ping": True,
    "pool_recycle": 280,
}

# --- Config JWT ---
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "change-moi-en-production")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=2)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
# Nécessaire pour que le callback de connexion unique (token_in_blocklist_loader
# dans auth.py) soit bien appelé sur chaque requête authentifiée.
app.config["JWT_BLOCKLIST_ENABLED"] = True
app.config["JWT_BLOCKLIST_TOKEN_CHECKS"] = ["access", "refresh"]

# --- Config token de vérification email / reset password ---
app.config["SECURITY_PASSWORD_SALT"] = os.environ.get("SECURITY_PASSWORD_SALT", "change-moi-aussi")
app.config["EMAIL_TOKEN_MAX_AGE_SECONDS"] = 60 * 60 * 24

# --- Config Flask-Mail ---
app.config["MAIL_SERVER"] = os.environ.get("MAIL_SERVER", "smtp-relay.brevo.com")
app.config["MAIL_PORT"] = int(os.environ.get("MAIL_PORT", 587))
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = os.environ.get("MAIL_DEFAULT_SENDER", "no-reply@votre-app.com")
# URL PUBLIQUE de votre logo pour l'en-tête des emails (ex: lien "raw" GitHub vers assets/logo.png).
# Un email ne peut pas charger un fichier local sur votre disque, il faut une URL accessible sur internet.
app.config["EMAIL_LOGO_URL"] = os.environ.get("EMAIL_LOGO_URL", "")
app.config["APP_BASE_URL"] = os.environ.get("APP_BASE_URL", "http://localhost:5000")

# 2. Initialisation de db avec app, puis de Migrate
db.init_app(app)
bcrypt.init_app(app)
jwt.init_app(app)
mail.init_app(app)
migrate = Migrate(app, db)

# Chargement des modèles pour la détection par Alembic / Flask-Migrate
import models

# --------------------------------------------------------
# 🔨 MIGRATION & CRÉATION DES TABLES POSTGRESQL
# --------------------------------------------------------
with app.app_context():
    db.create_all()
    # Ajout automatique des colonnes manquantes si la table existait déjà
    with db.engine.connect() as conn:
        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS xp INTEGER DEFAULT 0;"))
        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS avatar_base64 TEXT;"))
        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS current_session_id VARCHAR(255);"))
        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS total_parties INTEGER DEFAULT 0 NOT NULL;"))
        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS meilleur_score INTEGER DEFAULT 0 NOT NULL;"))
        conn.commit()
    print("✅ Base PostgreSQL à jour avec toutes les colonnes (statistiques incluses) !")
# --------------------------------------------------------

# 3. Enregistrement des routes d'authentification et de scores
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(scores_bp)

# ========================================================
# 🟢 ROUTE PING/PONG (Maintien en éveil Render)
# ========================================================
@app.route("/ping", methods=["GET"])
def ping():
    return "pong", 200

# ========================================================
# 🔌 INITIALISATION SOCKETIO & MOTEUR IA
# ========================================================
socketio = SocketIO(app, cors_allowed_origins="*")
ai_engine = AIGenerator()

# Dictionnaire des salons actifs :
# { "PIN": {"title": str, "players": [str], "questions": [], "current_question": 0, "teacher_name": str, "scores": dict} }
active_lobbies = {}

# Association sid (connexion socket) -> (pin, nom_joueur), pour retrouver la
# salle d'un joueur au moment de sa déconnexion (mode "party" uniquement).
sid_to_player = {}


def build_leaderboard(lobby):
    """Construit le classement complet : tous les joueurs de la salle,
    avec égalités = même rang (ex: 30, 20, 20 -> rangs 1, 2, 2).
    """
    scores = lobby.get("scores", {})
    noms = list(lobby.get("players", []))

    for nom_deja_note in scores.keys():
        if nom_deja_note not in noms:
            noms.append(nom_deja_note)

    entries = []
    for n in noms:
        info = scores.get(n, {})
        if isinstance(info, dict):
            score = info.get("score", 0)
            combo = info.get("combo", 0)
            avg_time = info.get("avg_time", 0)
        else:
            score = info
            combo = 0
            avg_time = 0
        entries.append(
            {"name": n, "score": score, "combo": combo, "avg_time": avg_time}
        )

    entries.sort(key=lambda p: p["score"], reverse=True)

    rang_actuel = 0
    score_precedent = None
    for i, p in enumerate(entries):
        if p["score"] != score_precedent:
            rang_actuel = i + 1
            score_precedent = p["score"]
        p["rank"] = rang_actuel

    return entries


@socketio.on("connect")
def handle_connect():
    print("🟢 Un client s'est connecté au serveur.")


@socketio.on("disconnect")
def handle_disconnect():
    info = sid_to_player.pop(request.sid, None)
    if info:
        pin, player = info
        lobby = active_lobbies.get(pin)
        if (
            lobby
            and lobby.get("mode") == "party"
            and lobby.get("party_started")
            and not lobby.get("quiz_ended_sent")
            and player not in lobby.get("abandoned", set())
        ):
            _programmer_abandon_differe(pin, player, delai=30.0)
    print("🔴 Un client s'est déconnecté du serveur.")


@socketio.on("create_room")
def handle_create_room(data):
    pin = data.get("pin", "").replace(" ", "")
    title = data.get("title", "Mon Quiz")

    active_lobbies[pin] = {
        "title": title,
        "players": [],
        "questions": [],
        "current_question": 0,
        "teacher_name": "Professeur",
        "scores": {},
    }
    join_room(pin)
    print(f"🎮 Salon créé : PIN [{pin}] | Titre : {title}")
    emit("room_created", {"success": True, "pin": pin})


@socketio.on("join_room")
def handle_join_room(data):
    pin = data.get("pin", "").replace(" ", "")
    player_name = data.get("name", "").strip()

    if pin in active_lobbies:
        if player_name not in active_lobbies[pin]["players"]:
            active_lobbies[pin]["players"].append(player_name)

        join_room(pin)

        # 1. Confirmer à l'élève (en incluant la liste actuelle des joueurs)
        emit(
            "join_response",
            {
                "success": True,
                "pin": pin,
                "title": active_lobbies[pin]["title"],
                "players": active_lobbies[pin]["players"],
            },
        )

        # 2. Prévenir le salon (prof et camarades)
        emit(
            "player_joined",
            {
                "name": player_name,
                "players": active_lobbies[pin]["players"],
            },
            to=pin,
        )
        print(f"✅ '{player_name}' a rejoint le salon [{pin}]")
    else:
        emit(
            "join_response",
            {
                "success": False,
                "message": f"❌ Salle introuvable pour le PIN '{pin}'.",
            },
        )
        print(f"❌ Échec : PIN [{pin}] inexistant.")


# ========================================================
# 🚀 DÉMARRAGE DU QUIZ ET TRANSMISSION DE LA 1ÈRE QUESTION
# ========================================================
@socketio.on("start_quiz")
def handle_start_quiz(data):
    pin = data.get("pin", "").replace(" ", "")
    questions = data.get("questions", [])
    teacher_name = data.get("teacher_name", "Professeur")
    title = data.get("title", "Mon Quiz")

    if pin in active_lobbies:
        active_lobbies[pin]["questions"] = questions
        active_lobbies[pin]["current_question"] = 0
        active_lobbies[pin]["teacher_name"] = teacher_name
        active_lobbies[pin]["title"] = title
        active_lobbies[pin]["answered_current"] = set()
        active_lobbies[pin]["quiz_ended_sent"] = False

        print(
            f"🚀 Lancement du quiz '{title}' par '{teacher_name}' pour le salon [{pin}] avec {len(questions)} questions"
        )

        # Diffuser à tous les élèves de la salle (avec teacher_name et title)
        emit(
            "quiz_started",
            {
                "pin": pin,
                "questions": questions,
                "current_question": 0,
                "teacher_name": teacher_name,
                "title": title,
            },
            to=pin,
        )


# ========================================================
# ⏭️ PASSAGE À LA QUESTION SUIVANTE (PROFESSEUR SEULEMENT)
# ========================================================
@socketio.on("next_question")
def handle_next_question(data):
    pin = data.get("pin", "").replace(" ", "")

    if pin in active_lobbies:
        lobby = active_lobbies[pin]
        lobby["current_question"] += 1
        lobby["answered_current"] = set()

        total_questions = len(lobby["questions"])
        current_index = lobby["current_question"]

        if current_index < total_questions:
            print(
                f"⏭️ Salon [{pin}] -> Passage à la question {current_index + 1}/{total_questions}"
            )
            # On informe TOUS les élèves du salon de changer de question
            emit("change_question", {"question_index": current_index}, to=pin)
        else:
            if not lobby.get("quiz_ended_sent"):
                print(f"🏁 Salon [{pin}] -> Quiz terminé (forcé par le prof) !")
                lobby["quiz_ended_sent"] = True
                leaderboard = build_leaderboard(lobby)
                emit("quiz_ended", {"pin": pin, "leaderboard": leaderboard}, to=pin)


# ========================================================
# 🛑 ANNULATION DU QUIZ PAR LE PROFESSEUR
# ========================================================
@socketio.on("cancel_quiz")
def handle_cancel_quiz(data):
    pin = data.get("pin", "").replace(" ", "")
    if pin in active_lobbies:
        print(f"🛑 Salon [{pin}] -> Quiz annulé par le professeur.")
        emit("quiz_cancelled", {"pin": pin}, to=pin)
        del active_lobbies[pin]


# ========================================================
# 📊 MISE À JOUR DU CLASSEMENT HÔTE EN TEMPS RÉEL
# ========================================================
@socketio.on("update_score")
def handle_update_score(data):
    pin = data.get("pin", "").replace(" ", "")
    player = data.get("player")
    score = data.get("score", 0)
    combo = data.get("combo", 0)
    avg_time = data.get("avg_time", 0)

    if pin in active_lobbies:
        lobby = active_lobbies[pin]
        lobby.setdefault("scores", {})
        lobby["scores"][player] = {
            "score": score,
            "combo": combo,
            "avg_time": avg_time,
        }

        leaderboard = build_leaderboard(lobby)
        emit("leaderboard_update", {"players": leaderboard}, to=pin)

        # Détection : dernière question + tout le monde a répondu -> fin synchronisée
        lobby.setdefault("answered_current", set())
        lobby["answered_current"].add(player)

        total_questions = len(lobby.get("questions", []))
        est_derniere_question = lobby.get("current_question", 0) >= total_questions - 1
        tout_le_monde_a_repondu = len(lobby["answered_current"]) >= len(lobby.get("players", []))

        if est_derniere_question and tout_le_monde_a_repondu and not lobby.get("quiz_ended_sent"):
            lobby["quiz_ended_sent"] = True
            print(f"🏁 Salon [{pin}] -> Tous les élèves ont terminé, fin synchronisée !")
            emit("quiz_ended", {"pin": pin, "leaderboard": leaderboard}, to=pin)


# ========================================================
# 🎉 MODE MULTIJOUEUR — NIVEAU 1 : "QUESTIONS ENTRE AMIS"
# ========================================================

PALIERS_DIFFICULTE = ["easy", "medium", "hard"]


def _normaliser_sujet(sujet):
    """Normalise un sujet pour détecter les doublons (espaces, casse)."""
    return " ".join((sujet or "").strip().lower().split())


def _construire_file_sujets(lobby):
    """Construit la liste des sujets UNIQUES (dédupliqués, ordre mélangé)
    à partir de tous les sujets proposés par les joueurs de la salle."""
    vus = set()
    sujets_dedup = []
    for sujet in lobby.get("subjects", {}).values():
        cle = _normaliser_sujet(sujet)
        if cle and cle not in vus:
            vus.add(cle)
            sujets_dedup.append(sujet.strip())
    random.shuffle(sujets_dedup)
    return sujets_dedup


@socketio.on("create_party_room")
def handle_create_party_room(data):
    """Créé une salle du Niveau 1. L'hôte propose déjà son propre sujet."""
    pin = data.get("pin", "").replace(" ", "")
    host_name = data.get("name", "").strip()
    subject = data.get("subject", "").strip()
    max_players = int(data.get("max_players") or 4)

    active_lobbies[pin] = {
        "mode": "party",
        "title": "Questions entre amis",
        "players": [host_name] if host_name else [],
        "subjects": {host_name: subject} if (host_name and subject) else {},
        "max_players": max_players,
        "current_question": 0,
        "teacher_name": host_name,
        "scores": {},
        "abandoned": set(),
        "party_started": False,
        "current_difficulty": "easy",
    }
    sid_to_player[request.sid] = (pin, host_name)
    join_room(pin)

    print(f"🎉 Salle 'Questions entre amis' créée : PIN [{pin}] par {host_name} | sujet: {subject} | cible: {max_players}")
    emit("room_created", {"success": True, "pin": pin})


@socketio.on("join_party_room")
def handle_join_party_room(data):
    """Rejoint une salle du Niveau 1 avec son propre sujet."""
    pin = data.get("pin", "").replace(" ", "")
    player_name = data.get("name", "").strip()
    subject = data.get("subject", "").strip()

    if pin not in active_lobbies or active_lobbies[pin].get("mode") != "party":
        emit("join_response", {"success": False, "message": f"❌ Salle introuvable pour le PIN '{pin}'."})
        return

    lobby = active_lobbies[pin]
    reconnexion = lobby.get("party_started") and player_name in lobby.get("players", [])

    if lobby.get("party_started") and not reconnexion:
        emit("join_response", {"success": False, "message": "❌ La partie a déjà commencé."})
        return

    if player_name not in lobby["players"]:
        lobby["players"].append(player_name)
    if subject and not lobby.get("party_started"):
        lobby.setdefault("subjects", {})[player_name] = subject

    sid_to_player[request.sid] = (pin, player_name)
    join_room(pin)

    if reconnexion:
        _annuler_abandon_differe(pin, player_name)
        lobby.get("abandoned", set()).discard(player_name)
        emit("join_response", {
            "success": True,
            "pin": pin,
            "title": lobby.get("title", "Questions entre amis"),
            "players": lobby["players"],
            "reconnexion": True,
            "current_question": lobby.get("current_question_data"),
            "question_index": lobby.get("current_question", 0),
        })
        print(f"🔌 '{player_name}' reconnecté à la salle party [{pin}].")
        return

    emit("join_response", {
        "success": True,
        "pin": pin,
        "title": lobby.get("title", "Questions entre amis"),
        "players": lobby["players"],
    })
    emit("player_joined", {"name": player_name, "players": lobby["players"]}, to=pin)
    print(f"✅ '{player_name}' a rejoint la salle party [{pin}] | sujet: {subject}")

    # Démarrage automatique 30s après avoir atteint l'effectif cible
    cible = lobby.get("max_players")
    if (
        cible
        and len(lobby["players"]) >= cible
        and not lobby.get("party_started")
        and not lobby.get("auto_start_scheduled")
    ):
        lobby["auto_start_scheduled"] = True
        print(f"⏳ Salle [{pin}] complète ({len(lobby['players'])}/{cible}) -> démarrage auto dans 30s.")
        emit("party_auto_start_scheduled", {"seconds": 30}, to=pin)
        timer = threading.Timer(30.0, _demarrer_partie_auto, args=(pin,))
        timer.daemon = True
        timer.start()


def _demarrer_partie_auto(pin):
    lobby = active_lobbies.get(pin)
    if lobby and not lobby.get("party_started"):
        socketio.emit("party_force_start", {}, to=pin)
        _lancer_partie(pin)


@socketio.on("start_party_quiz")
def handle_start_party_quiz(data):
    """Lancement manuel de la partie par l'hôte."""
    pin = data.get("pin", "").replace(" ", "")
    _lancer_partie(pin)


def _lancer_partie(pin):
    lobby = active_lobbies.get(pin)
    if not lobby or lobby.get("party_started"):
        return

    lobby["party_started"] = True
    lobby["subject_queue"] = _construire_file_sujets(lobby)
    lobby["current_difficulty"] = "easy"
    lobby["scores"] = {}
    lobby["answered_current"] = set()
    lobby["quiz_ended_sent"] = False
    lobby["current_question"] = 0

    if not lobby["subject_queue"]:
        socketio.emit("party_error", {"message": "Aucun sujet renseigné, impossible de lancer la partie."}, to=pin)
        lobby["party_started"] = False
        return

    print(f"🚀 Partie 'Questions entre amis' lancée pour [{pin}] — {len(lobby['subject_queue'])} sujet(s) en file")
    socketio.emit("party_started", {"pin": pin, "total_questions": len(lobby["subject_queue"])}, to=pin)
    _envoyer_prochaine_question_party(pin)


def _envoyer_prochaine_question_party(pin):
    lobby = active_lobbies.get(pin)
    if not lobby:
        return

    if not lobby["subject_queue"]:
        _terminer_partie(pin)
        return

    sujet = lobby["subject_queue"].pop(0)
    lobby["current_subject"] = sujet
    lobby["answered_current"] = set()
    lobby["party_stats_current"] = {"repondu": 0, "correct": 0}

    try:
        question = ai_engine.generate_single_question(sujet, lobby["current_difficulty"])
    except Exception as e:
        print(f"❌ Erreur génération IA pour le sujet '{sujet}': {e}")
        question = {
            "question": f"(Erreur IA, réessai auto au prochain sujet) — {sujet}",
            "A": "—", "B": "—", "C": "—", "D": "—",
            "correct": "A", "difficulty": lobby["current_difficulty"], "time": 20,
        }

    question["subject"] = sujet
    lobby["current_question_data"] = question
    lobby["current_question"] += 1
    total_restant = lobby["current_question"] + len(lobby["subject_queue"])

    socketio.emit("party_question", {
        "question": question,
        "question_index": lobby["current_question"],
        "total_questions": total_restant,
        "subject": sujet,
        "difficulty": lobby["current_difficulty"],
    }, to=pin)


@socketio.on("party_answer")
def handle_party_answer(data):
    """Réponse d'un joueur à une question du mode party."""
    pin = data.get("pin", "").replace(" ", "")
    player = data.get("player")
    correct = bool(data.get("correct", False))
    score = data.get("score", 0)
    combo = data.get("combo", 0)
    avg_time = data.get("avg_time", 0)

    lobby = active_lobbies.get(pin)
    if not lobby or not lobby.get("party_started"):
        return

    lobby.setdefault("scores", {})[player] = {"score": score, "combo": combo, "avg_time": avg_time}
    lobby.setdefault("answered_current", set()).add(player)

    stats = lobby.setdefault("party_stats_current", {"repondu": 0, "correct": 0})
    stats["repondu"] += 1
    if correct:
        stats["correct"] += 1

    leaderboard = build_leaderboard(lobby)
    emit("leaderboard_update", {"players": leaderboard}, to=pin)

    joueurs_actifs = [p for p in lobby["players"] if p not in lobby.get("abandoned", set())]
    if len(lobby["answered_current"]) >= len(joueurs_actifs) and joueurs_actifs:
        taux = stats["correct"] / stats["repondu"] if stats["repondu"] else 0
        idx = PALIERS_DIFFICULTE.index(lobby.get("current_difficulty", "easy"))
        if taux >= 0.7 and idx < len(PALIERS_DIFFICULTE) - 1:
            idx += 1
        elif taux < 0.4 and idx > 0:
            idx -= 1
        lobby["current_difficulty"] = PALIERS_DIFFICULTE[idx]
        print(f"📈 Salle [{pin}] -> taux de réussite {taux:.0%} sur la question précédente -> difficulté = '{lobby['current_difficulty']}'")

        _envoyer_prochaine_question_party(pin)


def _terminer_partie(pin, message=None):
    lobby = active_lobbies.get(pin)
    if not lobby or lobby.get("quiz_ended_sent"):
        return
    lobby["quiz_ended_sent"] = True
    leaderboard = build_leaderboard(lobby)
    payload = {"pin": pin, "leaderboard": leaderboard}
    if message:
        payload["message"] = message
    socketio.emit("quiz_ended", payload, to=pin)
    print(f"🏁 Salle [{pin}] terminée." + (f" ({message})" if message else ""))


def _programmer_abandon_differe(pin, player, delai=30.0):
    lobby = active_lobbies.get(pin)
    if not lobby:
        return

    timers = lobby.setdefault("pending_abandon_timers", {})
    ancien = timers.pop(player, None)
    if ancien:
        ancien.cancel()

    def _confirmer_abandon():
        lobby_actuel = active_lobbies.get(pin)
        if lobby_actuel and lobby_actuel.get("pending_abandon_timers", {}).pop(player, None) is not None:
            print(f"⏰ Délai de grâce (30s) écoulé pour '{player}' dans [{pin}] -> abandon confirmé.")
            _enregistrer_abandon(pin, player)

    timer = threading.Timer(delai, _confirmer_abandon)
    timer.daemon = True
    timers[player] = timer
    timer.start()
    print(f"🕒 '{player}' déconnecté de [{pin}] -> délai de grâce de {int(delai)}s avant abandon définitif.")


def _annuler_abandon_differe(pin, player):
    lobby = active_lobbies.get(pin)
    if not lobby:
        return
    timer = lobby.get("pending_abandon_timers", {}).pop(player, None)
    if timer:
        timer.cancel()
        print(f"🔌 '{player}' reconnecté à [{pin}] avant la fin du délai de grâce -> abandon annulé.")


def _enregistrer_abandon(pin, player):
    lobby = active_lobbies.get(pin)
    if not lobby or lobby.get("quiz_ended_sent"):
        return

    lobby.setdefault("abandoned", set()).add(player)
    print(f"🚪 '{player}' a abandonné la salle [{pin}] ({len(lobby['abandoned'])} abandon(s))")

    total_depart = len(lobby.get("players", [])) or 1
    if len(lobby["abandoned"]) / total_depart >= 0.75:
        _terminer_partie(pin, message="Partie arrêtée : trop de joueurs ont quitté.")


@socketio.on("player_abandon")
def handle_player_abandon(data):
    pin = data.get("pin", "").replace(" ", "")
    player = data.get("player")
    if pin in active_lobbies:
        _enregistrer_abandon(pin, player)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Serveur TMY Quiz Maker démarré sur le port {port}")
    socketio.run(app, host="0.0.0.0", port=port, debug=False)