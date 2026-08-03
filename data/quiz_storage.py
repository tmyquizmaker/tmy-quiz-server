"""
Bibliothèque "Mes Créations" — stockée sur le serveur, liée au compte connecté.
Garde exactement les mêmes noms de fonctions que l'ancienne version basée sur
un fichier local, pour ne rien casser dans my_quizzes.py / library_hub.py /
manual_quiz.py. Avant, tout était perdu à chaque rebuild du .exe (le dossier
data/ n'est pas persistant une fois empaqueté) — maintenant, l'utilisateur
retrouve ses quiz sur n'importe quel appareil où il se connecte.
"""
from auth_client import session


def load_quizzes():
    return session.lister_creations()


# Alias pour la compatibilité ascendante
load_all_quizzes = load_quizzes


def save_quiz(title, questions, teacher_name="Professeur", **kwargs):
    if not questions:
        print("⚠️ Sauvegarde annulée : Tentative d'enregistrer un quiz sans aucune question.")
        return None

    clean_title = (title or "").strip()
    if not clean_title or clean_title == "Quiz sans titre":
        print("⚠️ Sauvegarde annulée : Titre invalide ou 'Quiz sans titre'.")
        return None

    quiz = session.sauvegarder_creation(clean_title, questions, teacher_name)
    if quiz:
        print(f"✅ Quiz '{clean_title}' sauvegardé sur votre compte.")
    else:
        print(f"❌ Erreur lors de la sauvegarde du quiz '{clean_title}' (êtes-vous connecté ?).")
    return quiz


def delete_quiz(quiz_id):
    succes = session.supprimer_creation(quiz_id)
    if succes:
        print(f"🗑️ Quiz ID {quiz_id} supprimé avec succès.")
    else:
        print(f"⚠️ Impossible de supprimer le quiz ID {quiz_id}.")
    return succes


def clean_empty_quizzes():
    # Le serveur refuse déjà les quiz vides ou sans titre à la création (voir
    # library_routes.py) — rien à nettoyer côté client.
    return True
