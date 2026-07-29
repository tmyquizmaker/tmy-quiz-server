from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from extensions import db
from models import GameHistory, User, Quiz

scores_bp = Blueprint("scores", __name__)


@scores_bp.route("/quiz/<int:quiz_id>/score", methods=["POST"])
@jwt_required()
def enregistrer_score(quiz_id):
    data = request.get_json(silent=True) or {}
    score = data.get("score")
    duree = data.get("duree_secondes")

    if score is None or not isinstance(score, int):
        return jsonify({"error": "Le champ 'score' (entier) est requis"}), 400

    if not Quiz.query.get(quiz_id):
        return jsonify({"error": "Quiz introuvable"}), 404

    partie = GameHistory(
        user_id=get_jwt_identity(),
        quiz_id=quiz_id,
        score=score,
        duree_secondes=duree,
    )
    db.session.add(partie)
    db.session.commit()

    return jsonify({"message": "Score enregistré"}), 201


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
