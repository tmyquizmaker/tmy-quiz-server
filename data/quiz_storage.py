"""
===========================================
TMY Quiz Maker
Version 5.0

quiz_storage.py - Sauvegarde et Chargement des Quiz locaux
===========================================
"""

import json
import os

STORAGE_FILE = "saved_quizzes.json"

def save_quiz(quiz_title, questions):
    """Sauvegarde un quiz dans le fichier JSON local"""
    quizzes = load_all_quizzes()
    
    new_quiz = {
        "id": len(quizzes) + 1,
        "title": quiz_title,
        "total_questions": len(questions),
        "questions": questions
    }
    
    quizzes.append(new_quiz)
    
    with open(STORAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(quizzes, f, ensure_ascii=False, indent=4)
        
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