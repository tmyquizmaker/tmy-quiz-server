from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from extensions import db
from models import GameHistory, User, Quiz

scores_bp = Blueprint("scores", __name__)


@scores_bp.route("/me/xp", methods=["POST"])
@jwt_required()
def crediter_xp():
    """Crédite de l'XP sur le compte connecté, pour un quiz solo IA ou une
    partie 'Questions entre amis' — pas besoin de quiz_id (contrairement à
    /quiz/<id>/score) puisque ces quiz ne sont pas stockés dans la table Quiz."""
    data = request.get_json(silent=True) or {}
    xp_gagne = data.get("xp")
    score = data.get("score")

    if not isinstance(xp_gagne, int) or xp_gagne < 0:
        return jsonify({"error": "XP invalide"}), 400

    user = User.query.get(get_jwt_identity())
    if not user:
        return jsonify({"error": "Utilisateur introuvable"}), 404

    user.xp += xp_gagne
    user.total_parties += 1
    if isinstance(score, int) and score > user.meilleur_score:
        user.meilleur_score = score

    db.session.commit()

    return jsonify({
        "message": "XP créditée",
        "xp_gagne": xp_gagne,
        "user": user.to_public_dict(),
    }), 201


@scores_bp.route("/quiz/<int:quiz_id>/score", methods=["POST"])
@jwt_required()
def enregistrer_score(quiz_id):
    """Réservé aux quiz réellement stockés dans la table Quiz (bibliothèque
    partagée serveur, pas encore utilisée par les quiz générés par l'IA)."""
    data = request.get_json(silent=True) or {}
    score = data.get("score")
    duree = data.get("duree_secondes")

    if score is None or not isinstance(score, int):
        return jsonify({"error": "Le champ 'score' (entier) est requis"}), 400

    if not Quiz.query.get(quiz_id):
        return jsonify({"error": "Quiz introuvable"}), 404

    user = User.query.get(get_jwt_identity())
    if not user:
        return jsonify({"error": "Utilisateur introuvable"}), 404

    partie = GameHistory(
        user_id=user.id,
        quiz_id=quiz_id,
        score=score,
        duree_secondes=duree,
    )
    db.session.add(partie)

    user.xp += score
    user.total_parties += 1
    if score > user.meilleur_score:
        user.meilleur_score = score

    db.session.commit()

    return jsonify({
        "message": "Score enregistré",
        "xp_gagne": score,
        "user": user.to_public_dict(),
    }), 201


@scores_bp.route("/me/stats", methods=["GET"])
@jwt_required()
def mes_stats():
    """Statistiques personnelles de l'utilisateur connecté (pour la page Paramètres)."""
    user = User.query.get(get_jwt_identity())
    if not user:
        return jsonify({"error": "Utilisateur introuvable"}), 404

    return jsonify({
        "total_parties": user.total_parties,
        "meilleur_score": user.meilleur_score,
    }), 200


@scores_bp.route("/leaderboard", methods=["GET"])
def leaderboard_global():
    """Meilleur score de chaque utilisateur, tous quiz confondus, top 20.
    Ne nécessite pas d'être connecté : la page d'accueil peut l'afficher librement."""
    quiz_id = request.args.get("quiz_id", type=int)

    query = (
        db.session.query(
            User.username,
            db.func.max(GameHistory.score).label("meilleur_score"),
        )
        .join(GameHistory, GameHistory.user_id == User.id)
    )

    if quiz_id:
        query = query.filter(GameHistory.quiz_id == quiz_id)

    resultats = (
        query.group_by(User.username)
        .order_by(db.desc("meilleur_score"))
        .limit(20)
        .all()
    )

    return jsonify([
        {"username": username, "meilleur_score": meilleur_score}
        for username, meilleur_score in resultats
    ]), 200
