"""
Bibliothèque de quiz créés ('Mes Créations') et historique des parties jouées,
tous deux stockés côté serveur et strictement filtrés par owner_id — chaque
compte ne voit jamais les données d'un autre, sur aucun appareil.
"""
import json
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from extensions import db
from models import SavedQuiz, GameSession

library_bp = Blueprint("library", __name__)


# ==========================================================
# Mes Créations
# ==========================================================

@library_bp.route("/quizzes", methods=["POST"])
@jwt_required()
def creer_quiz():
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    teacher_name = data.get("teacher_name", "")
    questions = data.get("questions") or []

    if not title or title == "Quiz sans titre":
        return jsonify({"error": "Titre invalide"}), 400
    if not questions:
        return jsonify({"error": "Le quiz doit contenir au moins une question"}), 400

    quiz = SavedQuiz(
        owner_id=get_jwt_identity(),
        title=title,
        teacher_name=teacher_name,
        questions_json=json.dumps(questions, ensure_ascii=False),
    )
    db.session.add(quiz)
    db.session.commit()

    return jsonify({"message": "Quiz enregistré", "quiz": quiz.to_dict()}), 201


@library_bp.route("/quizzes", methods=["GET"])
@jwt_required()
def mes_quizzes():
    quizzes = (
        SavedQuiz.query.filter_by(owner_id=get_jwt_identity())
        .order_by(SavedQuiz.created_at.desc())
        .all()
    )
    return jsonify([q.to_dict() for q in quizzes]), 200


@library_bp.route("/quizzes/<int:quiz_id>", methods=["DELETE"])
@jwt_required()
def supprimer_quiz(quiz_id):
    quiz = SavedQuiz.query.get(quiz_id)
    if not quiz or quiz.owner_id != int(get_jwt_identity()):
        return jsonify({"error": "Quiz introuvable"}), 404
    db.session.delete(quiz)
    db.session.commit()
    return jsonify({"message": "Quiz supprimé"}), 200


@library_bp.route("/quizzes", methods=["DELETE"])
@jwt_required()
def supprimer_tous_quizzes():
    SavedQuiz.query.filter_by(owner_id=get_jwt_identity()).delete()
    db.session.commit()
    return jsonify({"message": "Tous les quiz supprimés"}), 200


# ==========================================================
# Historique des parties
# ==========================================================

@library_bp.route("/sessions", methods=["POST"])
@jwt_required()
def creer_session():
    data = request.get_json(silent=True) or {}

    row = GameSession(
        owner_id=get_jwt_identity(),
        session_code=data.get("session_id", ""),
        quiz_title=data.get("quiz_title", ""),
        niveau=data.get("niveau", ""),
        mode=data.get("mode", "Solo"),
        played_at=data.get("played_at", ""),
        score=data.get("score", ""),
        percentage=data.get("percentage", 0),
        xp=data.get("xp", 0),
        details_json=json.dumps(data.get("details", {}), ensure_ascii=False),
    )
    db.session.add(row)
    db.session.commit()

    return jsonify({"message": "Partie enregistrée", "session": row.to_dict()}), 201


@library_bp.route("/sessions", methods=["GET"])
@jwt_required()
def mes_sessions():
    sessions = (
        GameSession.query.filter_by(owner_id=get_jwt_identity())
        .order_by(GameSession.id.desc())
        .all()
    )
    return jsonify([s.to_dict() for s in sessions]), 200


@library_bp.route("/sessions/<session_code>", methods=["DELETE"])
@jwt_required()
def supprimer_session(session_code):
    row = GameSession.query.filter_by(
        owner_id=get_jwt_identity(), session_code=session_code
    ).first()
    if not row:
        return jsonify({"error": "Introuvable"}), 404
    db.session.delete(row)
    db.session.commit()
    return jsonify({"message": "Session supprimée"}), 200


@library_bp.route("/sessions", methods=["DELETE"])
@jwt_required()
def vider_sessions():
    GameSession.query.filter_by(owner_id=get_jwt_identity()).delete()
    db.session.commit()
    return jsonify({"message": "Historique vidé"}), 200
