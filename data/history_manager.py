"""
===========================================
TMY Quiz Maker
Version 4.1

history_manager.py - Gestionnaire d'historique TMY
===========================================
"""

import json
import os
from datetime import datetime
from auth_client import session

# Chemin absolu vers le fichier JSON dans le même dossier
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_FILE = os.path.join(BASE_DIR, "history.json")  # secours si personne n'est connecté


class HistoryManager:

    def __init__(self):
        # Chaque compte connecté a son propre fichier d'historique — jamais celui
        # d'un autre utilisateur, même sur le même appareil.
        if session.est_connecte() and session.user.get("username"):
            self.file = os.path.join(BASE_DIR, f"history_{session.user['username']}.json")
        else:
            self.file = HISTORY_FILE
        self.ensure_storage()

    # =====================================
    # Création / Vérification du stockage
    # =====================================
    def ensure_storage(self):
        folder = os.path.dirname(self.file)
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)

        if not os.path.exists(self.file):
            try:
                with open(self.file, "w", encoding="utf-8") as f:
                    json.dump([], f, indent=4, ensure_ascii=False)
            except Exception as e:
                print(f"❌ Erreur création history.json : {e}")

    # =====================================
    # Charger historique
    # =====================================
    def load_history(self):
        if not os.path.exists(self.file):
            return []
        try:
            with open(self.file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except Exception as e:
            print(f"❌ Erreur lors du chargement de l'historique : {e}")
            return []

    # =====================================
    # Créer les données résultat (Format TMY)
    # =====================================
    def create_quiz_data(
        self,
        sujet,
        niveau,
        score,
        total,
        xp=0,
        rank="Débutant",
        average_time=0,
        questions=None,
        mode="Solo"
    ):
        history = self.load_history()

        data = {
            "id": len(history) + 1,
            "mode": mode,
            "sujet": sujet,
            "niveau": niveau,
            "score": score,
            "total": total,
            "percentage": int((score / total) * 100) if total > 0 else 0,
            "xp": xp,
            "rank": rank,
            "average_time": average_time,
            "questions": questions or []
        }

        return data

    # =====================================
    # Sauvegarder un quiz terminé
    # =====================================
    def save_quiz(self, quiz_data):
        history = self.load_history()

        # Ajouter la date automatiquement si absente
        if "date" not in quiz_data:
            quiz_data["date"] = datetime.now().strftime("%d/%m/%Y %H:%M")

        # Insertion au début de la liste (index 0) pour un ordre chronologique inverse
        history.insert(0, quiz_data)

        try:
            with open(self.file, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=4, ensure_ascii=False)
            print(f"✅ Partie sauvegardée dans l'historique !")
            return True
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde : {e}")
            return False

    # =====================================
    # Derniers quiz enregistrés
    # =====================================
    def get_last_quizzes(self, limit=10):
        history = self.load_history()
        # Comme le fichier est maintenant trié du plus récent au plus ancien,
        # on prend directement les premiers éléments.
        return history[:limit]

    # =====================================
    # Anti-répétition IA
    # =====================================
    def get_used_questions(self):
        history = self.load_history()
        used_questions = []

        for quiz in history:
            questions = quiz.get("questions", [])
            for question in questions:
                if isinstance(question, dict):
                    text = question.get("question", "")
                    if text:
                        used_questions.append(text)
                elif isinstance(question, str):
                    used_questions.append(question)

        return used_questions[:100]

    # =====================================
    # Rechercher historique par sujet
    # =====================================
    def search_by_subject(self, subject):
        history = self.load_history()
        return [q for q in history if q.get("sujet", "").lower() == subject.lower()]

    # =====================================
    # Supprimer un quiz précis par son index
    # =====================================
    def delete_quiz(self, index):
        history = self.load_history()

        if 0 <= index < len(history):
            history.pop(index)
            try:
                with open(self.file, "w", encoding="utf-8") as f:
                    json.dump(history, f, indent=4, ensure_ascii=False)
                return True
            except Exception as e:
                print(f"❌ Erreur lors de la suppression : {e}")
                return False

        return False

    # =====================================
    # Effacer tout l'historique
    # =====================================
    def clear_all(self):
        try:
            with open(self.file, "w", encoding="utf-8") as f:
                json.dump([], f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ Erreur lors de la réinitialisation : {e}")
            return False

    # =====================================
    # Statistiques globales utilisateur
    # =====================================
    def get_statistics(self):
        history = self.load_history()

        if not history:
            return {
                "total_quiz": 0,
                "total_questions": 0,
                "total_xp": 0,
                "average_score": 0
            }

        total_quiz = len(history)
        total_questions = sum(q.get("total", 0) for q in history)
        total_xp = sum(q.get("xp", 0) for q in history)
        scores = [q.get("percentage", 0) for q in history]
        average_score = int(sum(scores) / len(scores)) if scores else 0

        return {
            "total_quiz": total_quiz,
            "total_questions": total_questions,
            "total_xp": total_xp,
            "average_score": average_score
        }