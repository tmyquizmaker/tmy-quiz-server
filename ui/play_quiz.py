"""
===========================================
TMY Quiz Maker
Version 5.0

play_quiz.py - Interface de jeu moderne & dynamique
===========================================
"""

import customtkinter as ctk
import winsound

from voice import parler, parler_sequence, stop
import ui.colors as colors
import ui.fonts as fonts


class PlayQuizPage(ctk.CTkFrame):

    def __init__(self, master, quiz, finish_callback):
        super().__init__(master)

        self.quiz = quiz
        self.finish_callback = finish_callback

        self.index = 0
        self.score = 0
        self.answered = False
        self.quiz_finished = False

        self.total_time = 0
        self.question_times = []
        self.fast_answers = 0
        self.time_out = 0
        self.total_xp = 0
        self.combo = 0
        self.max_combo = 0
        self.current_time = 0
        self.remaining_time = 0
        self.timer_running = False
        self.can_answer = False

        self.configure(fg_color=colors.BACKGROUND)

        # Conteneur principal
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(expand=True, fill="both", padx=40, pady=15)

        self.create_interface()
        self.load_question()

    # =========================================
    # Bruitages
    # =========================================
    def start_sound(self):
        winsound.Beep(1500, 400)

    def beep(self):
        winsound.Beep(1000, 200)

    def timeout_sound(self):
        winsound.Beep(500, 800)

    def correct_sound(self):
        winsound.Beep(1800, 200)

    def wrong_sound(self):
        winsound.Beep(350, 400)

    # =========================================
    # Création de l'interface
    # =========================================
    def create_interface(self):
        # -------------------------------------
        # 1. EN-TÊTE DASHBOARD
        # -------------------------------------
        self.header_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.header_frame.pack(fill="x", pady=(0, 10))

        # Titre App à gauche
        self.title_lbl = ctk.CTkLabel(
            self.header_frame,
            text="🧠 TMY QUIZ",
            font=("Arial", 16, "bold"),
            text_color="#1F6AA5"
        )
        self.title_lbl.pack(side="left")

        # Statut Rang / Combo / XP à droite
        self.stats_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.stats_frame.pack(side="right")

        # --- NOUVEAU : Label du Rang ---
        self.rank_label = ctk.CTkLabel(
            self.stats_frame,
            text="🥇 1er",
            font=("Arial", 13, "bold"),
            text_color="#00E676"
        )
        self.rank_label.pack(side="left", padx=(0, 10))

        self.combo_label = ctk.CTkLabel(
            self.stats_frame,
            text="🔥 x0",
            font=("Arial", 13, "bold"),
            text_color="#FF9800"
        )
        self.combo_label.pack(side="left", padx=(0, 10))

        self.xp_label = ctk.CTkLabel(
            self.stats_frame,
            text="⚡ 0 XP",
            font=("Arial", 13, "bold"),
            text_color="#FFD700"
        )
        self.xp_label.pack(side="left")

        # -------------------------------------
        # 2. PROGRESSION & CHRONOMÈTRE
        # -------------------------------------
        self.info_bar = ctk.CTkFrame(self.container, fg_color="transparent")
        self.info_bar.pack(fill="x", pady=(0, 5))

        self.counter = ctk.CTkLabel(
            self.info_bar,
            text="Question 1/10",
            font=("Arial", 14, "bold"),
            text_color="#FFFFFF"
        )
        self.counter.pack(side="left")

        self.timer_label = ctk.CTkLabel(
            self.info_bar,
            text="⏱ 0s",
            font=("Arial", 14, "bold"),
            text_color="#1F6AA5"
        )
        self.timer_label.pack(side="right")

        # Barre de progression du temps
        self.timer_bar = ctk.CTkProgressBar(
            self.container,
            height=8,
            corner_radius=4,
            progress_color="#1F6AA5",
            fg_color="#1E222D"
        )
        self.timer_bar.set(1)
        self.timer_bar.pack(fill="x", pady=(2, 15))

        # -------------------------------------
        # 3. CARTE DE LA QUESTION
        # -------------------------------------
        self.question_card = ctk.CTkFrame(
            self.container,
            fg_color="#1E222D",
            corner_radius=16,
            border_width=1,
            border_color="#2B303C"
        )
        self.question_card.pack(fill="x", ipady=15, pady=(0, 15))

        self.question = ctk.CTkLabel(
            self.question_card,
            text="Chargement de la question...",
            font=("Arial", 15, "bold"),
            text_color="#FFFFFF",
            wraplength=650,
            justify="center"
        )
        self.question.pack(expand=True, padx=25, pady=15)

        # -------------------------------------
        # 4. GRILLE DES RÉPONSES (Boutons paires)
        # -------------------------------------
        self.answers_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.answers_frame.pack(fill="both", expand=True)

        self.buttons = {}
        self.button_frames = {}

        for lettre in ["A", "B", "C", "D"]:
            # Frame de la réponse
            btn_frame = ctk.CTkFrame(
                self.answers_frame,
                fg_color="#1E222D",
                corner_radius=12,
                border_width=1,
                border_color="#2B303C"
            )
            btn_frame.pack(fill="x", pady=5)

            # Badge de lettre (A, B, C, D)
            badge = ctk.CTkLabel(
                btn_frame,
                text=lettre,
                font=("Arial", 12, "bold"),
                width=32,
                height=32,
                corner_radius=8,
                fg_color="#2B2D42",
                text_color="#FFFFFF"
            )
            badge.pack(side="left", padx=10, pady=8)

            # Bouton de texte
            bouton = ctk.CTkButton(
                btn_frame,
                text="",
                font=("Arial", 13),
                anchor="w",
                fg_color="transparent",
                hover_color="#252A37",
                text_color="#FFFFFF",
                command=lambda l=lettre: self.check_answer(l)
            )
            bouton.pack(side="left", fill="both", expand=True, padx=(0, 10))

            self.buttons[lettre] = bouton
            self.button_frames[lettre] = (btn_frame, badge)

        # -------------------------------------
        # 5. BOUTON SUIVANT
        # -------------------------------------
        self.next_button = ctk.CTkButton(
            self.container,
            text="QUESTION SUIVANTE →",
            font=("Arial", 13, "bold"),
            height=42,
            corner_radius=10,
            fg_color="#1F6AA5",
            hover_color="#144870",
            command=self.next_question
        )
        self.next_button.pack(fill="x", pady=(15, 0))

    # =========================================
    # Logique du temps & Questions
    # =========================================
    def calculate_time(self, question):
        texte = (
            question.get("question", "")
            + question.get("A", "")
            + question.get("B", "")
            + question.get("C", "")
            + question.get("D", "")
        )
        temps = 15
        if len(texte) > 200:
            temps += 10
        elif len(texte) > 100:
            temps += 5

        difficulte = question.get("difficulty", "medium")
        if difficulte == "hard":
            temps += 10
        elif difficulte == "easy":
            temps -= 3

        return max(10, min(60, temps))

    def calculate_live_rank(self):
        """Calcule dynamiquement le rang du joueur selon son taux de réussite et son combo"""
        accuracy = (self.score / (self.index + 1)) if self.index >= 0 else 1.0
        
        if accuracy >= 0.85 and self.combo >= 2:
            return "🥇 1er"
        elif accuracy >= 0.60:
            return "🥈 2ème"
        elif accuracy >= 0.40:
            return "🥉 3ème"
        else:
            return "📊 4ème"

    def load_question(self):
        self.answered = False

        if self.quiz_finished:
            return

        if self.index >= len(self.quiz):
            self.finish_quiz()
            return

        question = self.quiz[self.index]

        # Mettre à jour l'en-tête
        self.counter.configure(text=f"Question {self.index + 1} / {len(self.quiz)}")
        self.rank_label.configure(text=self.calculate_live_rank())
        self.combo_label.configure(text=f"🔥 x{self.combo}")
        self.xp_label.configure(text=f"⚡ {self.total_xp} XP")

        # Réinitialiser les boutons
        for lettre in ["A", "B", "C", "D"]:
            self.buttons[lettre].configure(text="", state="normal")
            frame, badge = self.button_frames[lettre]
            frame.configure(fg_color="#1E222D", border_color="#2B303C")
            badge.configure(fg_color="#2B2D42")

        # Affichage question
        texte_question = question.get("question", "")
        self.question.configure(text=texte_question)

        # Préparer le timer
        self.current_time = self.calculate_time(question)
        self.remaining_time = self.current_time
        self.timer_bar.set(1)
        self.update_timer_display()

        self.can_answer = False
        for btn in self.buttons.values():
            btn.configure(state="disabled")

        # Audio Cache & Lecture
        self.audio_cache = {
            "A": [("Petit A", 0.4), (question.get("A", ""), 0.4)],
            "B": [("Petit B", 0.4), (question.get("B", ""), 0.4)],
            "C": [("Petit C", 0.4), (question.get("C", ""), 0.4)],
            "D": [("Petit D", 0.4), (question.get("D", ""), 0.4)]
        }

        parler_sequence(
            [(texte_question, 0.3)],
            callback=lambda: self.after(0, self.lire_etape_A)
        )

    # --- Étapes Audio ---
    def lire_etape_A(self):
        if self.answered or self.quiz_finished: return
        self.buttons["A"].configure(text=self.quiz[self.index].get("A", ""))
        parler_sequence(self.audio_cache["A"], callback=lambda: self.after(0, self.lire_etape_B))

    def lire_etape_B(self):
        if self.answered or self.quiz_finished: return
        self.buttons["B"].configure(text=self.quiz[self.index].get("B", ""))
        parler_sequence(self.audio_cache["B"], callback=lambda: self.after(0, self.lire_etape_C))

    def lire_etape_C(self):
        if self.answered or self.quiz_finished: return
        self.buttons["C"].configure(text=self.quiz[self.index].get("C", ""))
        parler_sequence(self.audio_cache["C"], callback=lambda: self.after(0, self.lire_etape_D))

    def lire_etape_D(self):
        if self.answered or self.quiz_finished: return
        self.buttons["D"].configure(text=self.quiz[self.index].get("D", ""))
        parler_sequence(self.audio_cache["D"], callback=lambda: self.after(0, self.lire_etape_fin))

    def lire_etape_fin(self):
        if self.answered or self.quiz_finished: return
        texte_fin = f"Vous disposez maintenant de {self.current_time} secondes pour répondre"
        parler_sequence([(texte_fin, 0)], callback=lambda: self.after(0, self.start_timer))

    def start_timer(self):
        self.start_sound()
        self.can_answer = True
        for btn in self.buttons.values():
            btn.configure(state="normal")
        self.timer_running = True
        self.count_down()

    def count_down(self):
        if not self.timer_running or self.answered:
            return

        if self.remaining_time <= 0:
            self.timer_running = False
            self.timeout_sound()
            bonne = self.quiz[self.index]["correct"]
            parler(f"Temps écoulé. La bonne réponse était {bonne}.")
            self.time_out += 1
            self.combo = 0
            self.check_timeout()
            return

        self.update_timer_display()

        if 0 < self.remaining_time <= 5:
            self.beep()

        self.remaining_time -= 1
        self.after(1000, self.count_down)

    def check_timeout(self):
        if self.answered:
            return
        self.answered = True

        bonne = self.quiz[self.index]["correct"]
        frame, badge = self.button_frames[bonne]
        frame.configure(fg_color="#1E4620", border_color="#2E7D32")
        badge.configure(fg_color="#2E7D32")

        for btn in self.buttons.values():
            btn.configure(state="disabled")

        if self.index == len(self.quiz) - 1:
            self.after(1000, self.finish_quiz)

    def check_answer(self, lettre):
        stop()
        if not self.can_answer or self.answered:
            return

        self.answered = True
        self.timer_running = False
        self.stop_timer()

        temps_utilise = self.current_time - self.remaining_time

        # Calcul XP & Combo
        ratio = self.remaining_time / self.current_time
        xp = int(200 + (800 * ratio))

        difficulty = self.quiz[self.index].get("difficulty", "medium")
        multiplier = 1.6 if difficulty == "hard" else (1.0 if difficulty == "easy" else 1.3)
        xp = int(xp * multiplier)

        self.total_time += temps_utilise
        self.question_times.append(temps_utilise)

        if temps_utilise <= (self.current_time / 2):
            self.fast_answers += 1

        bonne = self.quiz[self.index]["correct"]

        if lettre == bonne:
            self.score += 1
            self.combo += 1
            if self.combo > self.max_combo:
                self.max_combo = self.combo

            bonus_table = {2: 50, 3: 100, 4: 150, 5: 250, 6: 350, 7: 500}
            bonus = bonus_table.get(self.combo, 700 if self.combo >= 8 else 0)
            self.total_xp += xp + bonus

            # Style réponse correcte (Vert)
            frame, badge = self.button_frames[lettre]
            frame.configure(fg_color="#1E4620", border_color="#2E7D32")
            badge.configure(fg_color="#2E7D32")

            self.correct_sound()
            parler("Bonne réponse.")
        else:
            # Style mauvaise réponse (Rouge)
            frame_w, badge_w = self.button_frames[lettre]
            frame_w.configure(fg_color="#4A151B", border_color="#C62828")
            badge_w.configure(fg_color="#C62828")

            # Afficher la bonne réponse en vert
            frame_c, badge_c = self.button_frames[bonne]
            frame_c.configure(fg_color="#1E4620", border_color="#2E7D32")
            badge_c.configure(fg_color="#2E7D32")

            self.combo = 0
            self.wrong_sound()
            parler(f"Mauvaise réponse. La bonne réponse était {bonne}.")

        # Mettre à jour l'affichage des stats
        self.rank_label.configure(text=self.calculate_live_rank())
        self.combo_label.configure(text=f"🔥 x{self.combo}")
        self.xp_label.configure(text=f"⚡ {self.total_xp} XP")

        for btn in self.buttons.values():
            btn.configure(state="disabled")

        if self.index == len(self.quiz) - 1:
            self.after(850, self.next_question)

    def next_question(self):
        if not self.answered:
            return
        self.timer_running = False
        self.index += 1

        if self.index >= len(self.quiz):
            self.finish_quiz()
        else:
            self.load_question()

    def finish_quiz(self):
        if self.quiz_finished:
            return

        self.quiz_finished = True
        self.timer_running = False
        total_questions = len(self.quiz)

        average_time = round(self.total_time / total_questions, 1) if total_questions > 0 else 0

        quiz_data = {
            "questions": self.quiz,
            "average_time": average_time,
            "total_time": self.total_time,
            "fast_answers": self.fast_answers,
            "time_out": self.time_out,
            "xp": self.calculate_xp()
        }

        parler(f"Quiz terminé. Vous avez obtenu {self.score} bonnes réponses sur {total_questions}.")

        self.finish_callback(
            self.score,
            total_questions,
            self.total_xp,
            self.max_combo,
            average_time,
            quiz_data
        )

    def calculate_xp(self):
        xp = self.score * 10 + self.fast_answers * 5
        if self.time_out == 0:
            xp += 20
        return xp

    def stop_timer(self):
        self.timer_running = False

    def update_timer_display(self):
        if self.current_time == 0:
            return

        ratio = max(0, self.remaining_time / self.current_time)
        self.timer_bar.set(ratio)
        self.timer_label.configure(text=f"⏱ {self.remaining_time}s")
        self.update_timer_color(ratio)

    def update_timer_color(self, ratio):
        if ratio <= 0.25:
            self.timer_label.configure(text_color="#FF5252")
            self.timer_bar.configure(progress_color="#FF5252")
        elif ratio <= 0.50:
            self.timer_label.configure(text_color="#FF9800")
            self.timer_bar.configure(progress_color="#FF9800")
        else:
            self.timer_label.configure(text_color="#1F6AA5")
            self.timer_bar.configure(progress_color="#1F6AA5")