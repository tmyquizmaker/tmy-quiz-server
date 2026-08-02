"""
===========================================
TMY Quiz Maker
Version 5.4 (Sécurité Anti-Quiz Vides)

quiz_storage.py - Sauvegarde, Chargement et Suppression des Quiz locaux
===========================================
"""

import json
import os
from datetime import datetime
from auth_client import session

# Dossier où sont rangés les fichiers de bibliothèque
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _get_quiz_file():
    """Chaque compte connecté a son propre fichier de bibliothèque — jamais celui
    d'un autre utilisateur, même sur le même appareil. Calculé à chaque appel
    (pas une constante) car l'utilisateur peut se connecter/déconnecter en cours d'app."""
    if session.est_connecte() and session.user.get("username"):
        nom_fichier = f"quizzes_{session.user['username']}.json"
    else:
        nom_fichier = "quizzes.json"  # secours si personne n'est connecté
    return os.path.join(BASE_DIR, nom_fichier)


def load_quizzes():
    """Charge tous les quiz enregistrés dans le fichier de bibliothèque de
    l'utilisateur connecté, en filtrant et nettoyant les données invalides."""
    quiz_file = _get_quiz_file()
    if not os.path.exists(quiz_file):
        return []
    try:
        with open(quiz_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            
            # S'assurer qu'on a bien une liste
            if not isinstance(data, list):
                return []
            
            # Aplatir et filtrer les données (peu importe le niveau d'imbrication)
            def _aplatir(elements):
                resultat = []
                for el in elements:
                    if isinstance(el, dict):
                        resultat.append(el)
                    elif isinstance(el, list):
                        resultat.extend(_aplatir(el))
                return resultat

            cleaned_quizzes = _aplatir(data)
                            
            # 🛑 SÉCURITÉ : Ne conserver que les VRAIS quiz qui ont au moins 1 question
            valid_quizzes = [
                q for q in cleaned_quizzes 
                if len(q.get("questions", [])) > 0 and q.get("title", "").strip() != "Quiz sans titre"
            ]
            
            return valid_quizzes
    except Exception as e:
        print(f"❌ Erreur lors du chargement des quiz : {e}")
        return []


# Alias pour la compatibilité ascendante
load_all_quizzes = load_quizzes


def save_quiz(title, questions, teacher_name="Professeur", **kwargs):
    """Sauvegarde ou met à jour un quiz dans le fichier JSON local avec garde-fou anti-vide"""
    
    # 🛑 SÉCURITÉ ABSOLUE : Si le quiz n'a aucune question ou n'a pas de nom valide, ON ANNULE
    if not questions or len(questions) == 0:
        print("⚠️ Sauvegarde annulée : Tentative d'enregistrer un quiz sans aucune question.")
        return None

    clean_title = (title or "").strip()
    if not clean_title or clean_title == "Quiz sans titre":
        print("⚠️ Sauvegarde annulée : Titre invalide ou 'Quiz sans titre'.")
        return None

    quizzes = load_quizzes()

    # Vérifier si un ID a été fourni pour mettre à jour un quiz existant
    quiz_id = kwargs.get("quiz_id") or kwargs.get("id")
    
    existing_quiz = None
    if quiz_id:
        for q in quizzes:
            if isinstance(q, dict) and q.get("id") == quiz_id:
                existing_quiz = q
                break

    if existing_quiz:
        # Mise à jour du quiz existant (garde la date de création d'origine)
        existing_quiz["title"] = clean_title
        existing_quiz["teacher_name"] = teacher_name
        existing_quiz["total_questions"] = len(questions)
        existing_quiz["questions"] = questions
        if "created_at" not in existing_quiz:
            existing_quiz["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        saved_entry = existing_quiz
    else:
        # Création d'un nouvel ID unique (max ID + 1)
        existing_ids = [q.get("id", 0) for q in quizzes if isinstance(q, dict)]
        next_id = max(existing_ids) + 1 if existing_ids else 1

        saved_entry = {
            "id": next_id,
            "title": clean_title,
            "teacher_name": teacher_name,
            "total_questions": len(questions),
            "questions": questions,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        quizzes.append(saved_entry)

    try:
        with open(_get_quiz_file(), "w", encoding="utf-8") as f:
            json.dump(quizzes, f, ensure_ascii=False, indent=4)
        print(f"✅ Quiz '{clean_title}' sauvegardé avec succès par {teacher_name}.")
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde du quiz : {e}")

    return saved_entry


def delete_quiz(quiz_id):
    """Supprime un quiz de la liste via son ID"""
    quizzes = load_quizzes()
    
    # Filtrer pour supprimer le quiz correspondant
    updated_quizzes = [q for q in quizzes if isinstance(q, dict) and q.get("id") != quiz_id]

    if len(updated_quizzes) == len(quizzes):
        print(f"⚠️ Aucun quiz trouvé avec l'ID {quiz_id}.")
        return False

    try:
        with open(_get_quiz_file(), "w", encoding="utf-8") as f:
            json.dump(updated_quizzes, f, ensure_ascii=False, indent=4)
        print(f"🗑️ Quiz ID {quiz_id} supprimé avec succès.")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la suppression du quiz : {e}")
        return False


def clean_empty_quizzes():
    """Supprime définitivement tous les quiz vides ou 'Quiz sans titre' du fichier JSON"""
    quiz_file = _get_quiz_file()
    if not os.path.exists(quiz_file):
        return True
        
    try:
        with open(quiz_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            return False

        filtered = [
            q for q in data 
            if isinstance(q, dict) and len(q.get("questions", [])) > 0 and q.get("title", "").strip() not in ["", "Quiz sans titre"]
        ]

        with open(quiz_file, "w", encoding="utf-8") as f:
            json.dump(filtered, f, ensure_ascii=False, indent=4)
        print("🧹 Nettoyage des quiz vides effectué avec succès.")
        return True
    except Exception as e:
        print(f"❌ Erreur lors du nettoyage : {e}")
        return False