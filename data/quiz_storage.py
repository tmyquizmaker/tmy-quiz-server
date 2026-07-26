"""
===========================================
TMY Quiz Maker
Version 5.2

quiz_storage.py - Sauvegarde et Chargement des Quiz locaux
===========================================
"""

import json
import os

STORAGE_FILE = "saved_quizzes.json"

def save_quiz(quiz_title, questions, teacher_name="Professeur", **kwargs):
    """Sauvegarde un quiz dans le fichier JSON local en incluant le nom de l'auteur/professeur"""
    quizzes = load_all_quizzes()
    
    new_quiz = {
        "id": len(quizzes) + 1,
        "title": quiz_title,
        "teacher": teacher_name,
        "total_questions": len(questions),
        "questions": questions
    }
    
    quizzes.append(new_quiz)
    
    try:
        with open(STORAGE_FILE, "w", encoding="utf-8") as f:
            json.dump(quizzes, f, ensure_ascii=False, indent=4)
        print(f"✅ Quiz '{quiz_title}' sauvegardé avec succès par {teacher_name}.")
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde du quiz : {e}")
        
    return new_quiz

def load_all_quizzes():
    """Charge tous les quiz enregistrés"""
    if not os.path.exists(STORAGE_FILE):
        return []
    try:
        with open(STORAGE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []