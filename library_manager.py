import json
import os
from datetime import datetime
from auth_client import session


def _fichier_creations():
    """Chaque compte connecté a son propre fichier — jamais celui d'un autre utilisateur."""
    if session.est_connecte() and session.user.get("username"):
        return os.path.join("data", f"saved_quizzes_{session.user['username']}.json")
    return os.path.join("data", "saved_quizzes.json")


def _fichier_historique():
    """Chaque compte connecté a son propre historique de parties jouées."""
    if session.est_connecte() and session.user.get("username"):
        return os.path.join("data", f"game_sessions_{session.user['username']}.json")
    return os.path.join("data", "history.json")


class LibraryManager:
    @staticmethod
    def _ensure_data_folder():
        os.makedirs("data", exist_ok=True)

    # ------------------ MES CRÉATIONS (QUIZ CRÉÉS) ------------------
    @classmethod
    def get_creations(cls):
        cls._ensure_data_folder()
        path = _fichier_creations()
        if not os.path.exists(path):
            return []
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Sécurité : Ajoute une date par défaut aux anciens quiz qui n'en ont pas
                for quiz in data:
                    if "created_at" not in quiz:
                        quiz["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                return data
        except Exception:
            return []

    @classmethod
    def delete_creation(cls, quiz_id):
        path = _fichier_creations()
        creations = cls.get_creations()
        creations = [q for q in creations if q.get("id") != quiz_id]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(creations, f, ensure_ascii=False, indent=4)

    @classmethod
    def delete_all_creations(cls):
        path = _fichier_creations()
        with open(path, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=4)

    # ------------------ HISTORIQUE DES PARTIES (QUIZ JOUÉS) ------------------
    @classmethod
    def get_history(cls):
        cls._ensure_data_folder()
        path = _fichier_historique()
        if not os.path.exists(path):
            return []
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    @classmethod
    def save_game_session(cls, session_data):
        """
        Structure attendue pour session_data:
        {
            "session_id": "SESSION_12345",
            "quiz_title": "Géographie",
            "mode": "Solo" ou "Multijoueur",
            "played_at": "2026-07-28 14:30:00",
            "score": "16/20",
            "percentage": 80,
            "details": {
                "correct": [{"question": "...", "your_answer": "..."}],
                "wrong": [{"question": "...", "your_answer": "...", "correct_answer": "..."}],
                "unanswered": [{"question": "..."}]
            }
        }
        """
        path = _fichier_historique()
        history = cls.get_history()
        history.insert(0, session_data)  # Ajoute au début (le plus récent)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=4)

    @classmethod
    def delete_history_session(cls, session_id):
        path = _fichier_historique()
        history = cls.get_history()
        history = [s for s in history if s.get("session_id") != session_id]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=4)

    @classmethod
    def clear_history(cls):
        path = _fichier_historique()
        with open(path, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=4)
