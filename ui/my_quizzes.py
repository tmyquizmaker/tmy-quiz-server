"""
===========================================
TMY Quiz Maker
Version 5.0

my_quizzes.py - Page 'Mes Quiz' préparés
===========================================
"""

import customtkinter as ctk
from data.quiz_storage import load_all_quizzes

class MyQuizzesPage(ctk.CTkFrame):

    def __init__(self, master, launch_lobby_callback, back_callback):
        super().__init__(master, fg_color="#121620")

        self.launch_lobby_callback = launch_lobby_callback
        self.back_callback = back_callback

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(expand=True, fill="both", padx=30, pady=20)

        # En-tête
        self.top_bar = ctk.CTkFrame(self.container, fg_color="#1E222D", corner_radius=12)
        self.top_bar.pack(fill="x", pady=(0, 15), ipady=5)

        self.back_btn = ctk.CTkButton(
            self.top_bar, text="← Retour", width=80, fg_color="#2B2D42",
            hover_color="#3A3D52", command=self.back_callback
        )
        self.back_btn.pack(side="left", padx=15)

        self.title_lbl = ctk.CTkLabel(self.top_bar, text="📁 MES QUIZ ENREGISTRÉS", font=("Arial", 16, "bold"), text_color="#FFFFFF")
        self.title_lbl.pack(side="left", padx=10)

        # Liste des quiz
        self.scroll_frame = ctk.CTkScrollableFrame(self.container, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True)

        self.load_quizzes()

    def load_quizzes(self):
        quizzes = load_all_quizzes()

        if not quizzes:
            empty_lbl = ctk.CTkLabel(self.scroll_frame, text="Aucun quiz enregistré pour l'instant.\nCréez-en un depuis le menu principal !", font=("Arial", 14), text_color="#AAAAAA")
            empty_lbl.pack(pady=50)
            return

        for quiz in quizzes:
            card = ctk.CTkFrame(self.scroll_frame, fg_color="#1E222D", corner_radius=12, border_width=1, border_color="#2B303C")
            card.pack(fill="x", pady=8, ipady=5)

            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.pack(side="left", padx=20, pady=10)

            q_title = ctk.CTkLabel(info_frame, text=quiz['title'], font=("Arial", 14, "bold"), text_color="#FFFFFF")
            q_title.pack(anchor="w")

            q_sub = ctk.CTkLabel(info_frame, text=f"{quiz['total_questions']} Questions", font=("Arial", 11), text_color="#8A8F9E")
            q_sub.pack(anchor="w")

            # Bouton de lancement de salon
            launch_btn = ctk.CTkButton(
                card, text="▶ LANCER EN CLASSE (LOBBY)", font=("Arial", 12, "bold"),
                fg_color="#2E7D32", hover_color="#1E4620", height=38,
                command=lambda q=quiz: self.launch_lobby_callback(q['title'], q['questions'], q.get('teacher', 'Professeur'))
            )
            launch_btn.pack(side="right", padx=20)