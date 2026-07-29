"""
===========================================
TMY Quiz Maker
Version 5.0

manual_quiz.py - Éditeur de Quiz Manuel Révolutionnaire
===========================================
"""

import customtkinter as ctk

class ManualQuizPage(ctk.CTkFrame):

    def __init__(self, master, on_quiz_created, back_callback):
        super().__init__(master, fg_color="#121620")

        self.on_quiz_created = on_quiz_created
        self.back_callback = back_callback

        # Liste des questions du quiz
        self.questions = [self.get_empty_question(1)]
        self.current_q_index = 0

        # Conteneur principal
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(expand=True, fill="both", padx=25, pady=20)

        # ---------------------------------------------
        # 1. BARRE SUPÉRIEURE (Titre, Nom du Prof & Actions)
        # ---------------------------------------------
        self.top_bar = ctk.CTkFrame(self.container, fg_color="#1E222D", corner_radius=12)
        self.top_bar.pack(fill="x", pady=(0, 15), ipady=5)

        self.back_btn = ctk.CTkButton(
            self.top_bar, text="← Retour", width=80, fg_color="#2B2D42",
            hover_color="#3A3D52", command=self.back_callback
        )
        self.back_btn.pack(side="left", padx=15)

        # INPUT 1 : Titre du Quiz
        self.quiz_title_entry = ctk.CTkEntry(
            self.top_bar, placeholder_text="Titre de ton Quiz (ex: Master History 2026)",
            font=("Arial", 13, "bold"), width=280, fg_color="#121620", border_color="#2B303C"
        )
        self.quiz_title_entry.pack(side="left", padx=5, expand=True, fill="x")

        # INPUT 2 : Nom du Professeur
        self.prof_name_entry = ctk.CTkEntry(
            self.top_bar, placeholder_text="Nom du Prof (ex: Prof. Dubois)",
            font=("Arial", 13, "bold"), width=200, fg_color="#121620", border_color="#2B303C"
        )
        self.prof_name_entry.pack(side="left", padx=10)

        self.finish_btn = ctk.CTkButton(
            self.top_bar, text="🚀 TERMINER & GÉNÉRER LE PIN",
            font=("Arial", 12, "bold"), fg_color="#2E7D32", hover_color="#1E4620",
            height=38, command=self.finish_quiz_creation
        )
        self.finish_btn.pack(side="right", padx=15)

        # ---------------------------------------------
        # 2. ZONE CENTRALE (Sidebar Liste + Formulaire)
        # ---------------------------------------------
        self.main_body = ctk.CTkFrame(self.container, fg_color="transparent")
        self.main_body.pack(fill="both", expand=True)

        # --- SIDEBAR GAUCHE (Navigation Questions) ---
        self.sidebar = ctk.CTkFrame(self.main_body, fg_color="#1E222D", corner_radius=12, width=200)
        self.sidebar.pack(side="left", fill="y", padx=(0, 15))

        self.sidebar_title = ctk.CTkLabel(self.sidebar, text="QUESTIONS", font=("Arial", 12, "bold"), text_color="#8A8F9E")
        self.sidebar_title.pack(pady=(15, 10))

        self.q_list_frame = ctk.CTkScrollableFrame(self.sidebar, fg_color="transparent", width=170)
        self.q_list_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.add_q_btn = ctk.CTkButton(
            self.sidebar, text="+ Nouvelle Question", fg_color="#1F6AA5",
            hover_color="#144870", command=self.add_new_question
        )
        self.add_q_btn.pack(fill="x", padx=10, pady=15)

        # --- FORMULAIRE CENTRAL DE LA QUESTION ---
        self.form_card = ctk.CTkFrame(self.main_body, fg_color="#1E222D", corner_radius=16, border_width=1, border_color="#2B303C")
        self.form_card.pack(side="right", fill="both", expand=True)

        self.form_content = ctk.CTkFrame(self.form_card, fg_color="transparent")
        self.form_content.pack(fill="both", expand=True, padx=25, pady=20)

        # Input Intitulé Question
        self.q_label_title = ctk.CTkLabel(self.form_content, text="Intitulé de la question :", font=("Arial", 12, "bold"), text_color="#FFFFFF")
        self.q_label_title.pack(anchor="w", pady=(0, 5))

        self.question_text = ctk.CTkEntry(
            self.form_content, placeholder_text="Tape ta question ici...",
            font=("Arial", 14), fg_color="#121620", border_color="#2B303C", height=45
        )
        self.question_text.pack(fill="x", pady=(0, 15))

        # Configs secondaires (Timer + Points)
        self.config_frame = ctk.CTkFrame(self.form_content, fg_color="transparent")
        self.config_frame.pack(fill="x", pady=(0, 15))

        # Temps par question
        self.timer_lbl = ctk.CTkLabel(self.config_frame, text="⏱ Minuteur :", font=("Arial", 11, "bold"), text_color="#AAAAAA")
        self.timer_lbl.pack(side="left", padx=(0, 5))
        self.timer_opt = ctk.CTkOptionMenu(
            self.config_frame, values=["10s", "15s", "20s", "30s", "60s"],
            width=80, fg_color="#121620", button_color="#2B303C"
        )
        self.timer_opt.set("20s")
        self.timer_opt.pack(side="left", padx=(0, 20))

        # Points
        self.points_lbl = ctk.CTkLabel(self.config_frame, text="🏆 Points :", font=("Arial", 11, "bold"), text_color="#AAAAAA")
        self.points_lbl.pack(side="left", padx=(0, 5))
        self.points_entry = ctk.CTkEntry(
            self.config_frame, width=70, fg_color="#121620", border_color="#2B303C",
            placeholder_text="10"
        )
        self.points_entry.pack(side="left")

        # ---------------------------------------------
        # 3. GRILLE DES 4 RÉPONSES
        # ---------------------------------------------
        self.answers_lbl = ctk.CTkLabel(self.form_content, text="Options de réponse (Clique sur la lettre pour définir la BONNE réponse) :", font=("Arial", 11, "bold"), text_color="#FFFFFF")
        self.answers_lbl.pack(anchor="w", pady=(10, 8))

        self.answers_entries = {}
        self.correct_buttons = {}
        self.selected_correct = "A"

        for lettre in ["A", "B", "C", "D"]:
            row_frame = ctk.CTkFrame(self.form_content, fg_color="transparent")
            row_frame.pack(fill="x", pady=4)

            # Bouton badge Correct
            btn_badge = ctk.CTkButton(
                row_frame, text=lettre, width=36, height=36, corner_radius=8,
                font=("Arial", 12, "bold"), fg_color="#2E7D32" if lettre == "A" else "#2B2D42",
                command=lambda l=lettre: self.set_correct_answer(l)
            )
            btn_badge.pack(side="left", padx=(0, 10))
            self.correct_buttons[lettre] = btn_badge

            # Input Réponse
            entry = ctk.CTkEntry(
                row_frame, placeholder_text=f"Réponse {lettre}",
                fg_color="#121620", border_color="#2B303C", height=36
            )
            entry.pack(side="left", fill="x", expand=True)
            self.answers_entries[lettre] = entry

        # Charger la première question par défaut
        self.render_sidebar()
        self.load_question_to_form(0)

    def load_quiz(self, quiz_data):
        """Charge un quiz existant dans les champs d'édition."""
        if not quiz_data:
            return

        # 1. Charger le titre et le nom de l'auteur/professeur
        title = quiz_data.get("title", "")
        teacher = quiz_data.get("teacher_name", "")

        if hasattr(self, "quiz_title_entry"):
            self.quiz_title_entry.delete(0, "end")
            self.quiz_title_entry.insert(0, title)

        if hasattr(self, "prof_name_entry"):
            self.prof_name_entry.delete(0, "end")
            self.prof_name_entry.insert(0, teacher)

        # 2. Récupérer et charger la liste des questions
        questions_input = quiz_data.get("questions", [])

        if questions_input:
            # Réinitialise la liste locale
            self.questions = list(questions_input)
            self.current_q_index = 0

            # Affiche directement la première question SANS sauvegarder par-dessus
            # (sinon ça écraserait la question tout juste chargée avec les vieux champs vides)
            self.populate_form(0)

    def get_empty_question(self, index):
        return {
            "question": f"Question {index}",
            "A": "", "B": "", "C": "", "D": "",
            "correct": "A", "time": "20s", "points": "10"
        }

    def save_current_form_data(self):
        """Enregistre les saisis actuelles dans la structure de données"""
        if not self.questions or self.current_q_index >= len(self.questions):
            return

        q = self.questions[self.current_q_index]
        q["question"] = self.question_text.get()
        q["A"] = self.answers_entries["A"].get()
        q["B"] = self.answers_entries["B"].get()
        q["C"] = self.answers_entries["C"].get()
        q["D"] = self.answers_entries["D"].get()
        q["correct"] = self.selected_correct
        q["time"] = self.timer_opt.get()
        q["points"] = self.points_entry.get().strip() or "10"

    def populate_form(self, index):
        """Affiche uniquement les données de la question à l'écran, SANS rien sauvegarder avant
        (utilisé lors du chargement initial d'un quiz existant)."""
        self.current_q_index = index

        if not self.questions or index >= len(self.questions):
            return

        q = self.questions[index]

        self.question_text.delete(0, "end")
        self.question_text.insert(0, q.get("question", ""))

        for lettre in ["A", "B", "C", "D"]:
            self.answers_entries[lettre].delete(0, "end")
            self.answers_entries[lettre].insert(0, q.get(lettre, ""))

        self.set_correct_answer(q.get("correct", "A"))
        self.timer_opt.set(q.get("time", "20s"))
        self.points_entry.delete(0, "end")
        self.points_entry.insert(0, str(q.get("points", "10")))

        self.render_sidebar()

    def load_question_to_form(self, index):
        """Charge une question dans les champs (sauvegarde d'abord la question en cours)."""
        self.save_current_form_data()
        self.populate_form(index)

    def set_correct_answer(self, lettre):
        self.selected_correct = lettre
        for l, btn in self.correct_buttons.items():
            if l == lettre:
                btn.configure(fg_color="#2E7D32")
            else:
                btn.configure(fg_color="#2B2D42")

    def add_new_question(self):
        self.save_current_form_data()
        new_idx = len(self.questions)
        self.questions.append(self.get_empty_question(new_idx + 1))
        self.load_question_to_form(new_idx)

    def render_sidebar(self):
        for w in self.q_list_frame.winfo_children():
            w.destroy()

        for i, q in enumerate(self.questions):
            is_active = (i == self.current_q_index)
            btn = ctk.CTkButton(
                self.q_list_frame,
                text=f"Q{i+1}. {q.get('question', '')[:12]}...",
                font=("Arial", 11, "bold" if is_active else "normal"),
                fg_color="#1F6AA5" if is_active else "#121620",
                hover_color="#144870",
                height=32,
                command=lambda idx=i: self.load_question_to_form(idx)
            )
            btn.pack(fill="x", pady=2)

    def finish_quiz_creation(self):
        """Valide et transmet le quiz terminé avec le nom du prof"""
        self.save_current_form_data()
        
        title = self.quiz_title_entry.get().strip() or "Mon Quiz Personnalisé"
        teacher_name = self.prof_name_entry.get().strip() or "Professeur Anonyme"

        self.on_quiz_created(
            quiz_title=title, 
            teacher_name=teacher_name, 
            quiz_data=self.questions
        )