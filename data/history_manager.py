"""
===========================================
TMY Quiz Maker
Version 4.0

history_manager.py

Gestionnaire historique TMY

Fonctions :
- Sauvegarder les quiz terminés
- Charger les anciens résultats
- Préparer anti-répétition IA
- Compatible Android futur
===========================================
"""


import json
import os
from datetime import datetime



class HistoryManager:



    def __init__(self):


        self.folder = "data"


        self.file = os.path.join(

            self.folder,

            "history.json"

        )

        os.makedirs(

            self.folder,

            exist_ok=True

        )


        if not os.path.exists(self.file):


            with open(

                self.file,

                "w",

                encoding="utf-8"

            ) as f:


                json.dump(

                    [],

                    f,

                    indent=4,

                    ensure_ascii=False

                )

        self.ensure_storage()





    # =====================================
    # Création stockage
    # =====================================


    def ensure_storage(self):


        if not os.path.exists(self.folder):


            os.makedirs(

                self.folder

            )



        if not os.path.exists(self.file):


            with open(

                self.file,

                "w",

                encoding="utf-8"

            ) as f:


                json.dump(

                    [],

                    f,

                    indent=4,

                    ensure_ascii=False

                )





    # =====================================
    # Charger historique
    # =====================================


    def load_history(self):


        try:


            with open(

                self.file,

                "r",

                encoding="utf-8"

            ) as f:


                return json.load(f)



        except Exception:


            return []
        
            # =====================================
    # Sauvegarder un quiz terminé
    # =====================================


    def save_quiz(self, quiz_data):


        history = self.load_history()



        # Ajouter date automatiquement

        quiz_data["date"] = datetime.now().strftime(

            "%d/%m/%Y %H:%M"

        )



        history.append(

            quiz_data

        )



        with open(

            self.file,

            "w",

            encoding="utf-8"

        ) as f:


            json.dump(

                history,

                f,

                indent=4,

                ensure_ascii=False

            )



        return True





    # =====================================
    # Créer les données résultat
    # Format standard TMY
    # =====================================


    def create_quiz_data(

            self,

            sujet,

            niveau,

            score,

            total,

            xp,

            rank,

            average_time,

            questions=None

    ):



        data = {


            "sujet": sujet,


            "niveau": niveau,


            "score": score,


            "total": total,


            "percentage": int(

                (score / total) * 100

            ) if total > 0 else 0,


            "xp": xp,


            "rank": rank,


            "average_time": average_time,


            "questions": questions or []

        }



        return data





    # =====================================
    # Derniers quiz
    # =====================================


    def get_last_quizzes(

            self,

            limit=10

    ):


        history = self.load_history()



        return history[-limit:]

            # =====================================
    # Récupérer toutes les questions déjà vues
    # Pour IA anti-répétition
    # =====================================


    def get_used_questions(self):


        history = self.load_history()


        used_questions = []



        for quiz in history:


            questions = quiz.get(

                "questions",

                []

            )


            for question in questions:


                if isinstance(question, dict):


                    text = question.get(

                        "question",

                        ""

                    )


                    if text:


                        used_questions.append(

                            text

                        )


                else:


                    used_questions.append(

                        question

                    )



        return used_questions[-100:]





    # =====================================
    # Rechercher historique par sujet
    # =====================================


    def search_by_subject(

            self,

            subject

    ):


        history = self.load_history()



        result = []



        for quiz in history:


            if quiz.get(

                "sujet",

                ""

            ).lower() == subject.lower():


                result.append(

                    quiz

                )



        return result





    # =====================================
    # Supprimer un quiz précis
    # =====================================


    def delete_quiz(

            self,

            index

    ):


        history = self.load_history()



        if 0 <= index < len(history):


            history.pop(index)



            with open(

                self.file,

                "w",

                encoding="utf-8"

            ) as f:


                json.dump(

                    history,

                    f,

                    indent=4,

                    ensure_ascii=False

                )


            return True



        return False





    # =====================================
    # Effacer tout historique
    # =====================================


    def clear_all(self):


        with open(

            self.file,

            "w",

            encoding="utf-8"

        ) as f:


            json.dump(

                [],

                f,

                indent=4,

                ensure_ascii=False

            )



        return True





    # =====================================
    # Statistiques globales utilisateur
    # =====================================


    def get_statistics(self):


        history = self.load_history()



        if len(history) == 0:


            return {


                "total_quiz": 0,

                "total_questions": 0,

                "total_xp": 0,

                "average_score": 0

            }



        total_quiz = len(history)


        total_questions = sum(

            q.get(

                "total",

                0

            )

            for q in history

        )


        total_xp = sum(

            q.get(

                "xp",

                0

            )

            for q in history

        )



        scores = [


            q.get(

                "percentage",

                0

            )

            for q in history


        ]



        average_score = int(

            sum(scores) / len(scores)

        )



        return {


            "total_quiz": total_quiz,

            "total_questions": total_questions,

            "total_xp": total_xp,

            "average_score": average_score

        }